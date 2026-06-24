// wonder_eye - カメラ映像をAIで解析し、興味ある方向に首を向けるStack-chan
//
// References:
// https://github.com/GOB52/gob_GC0308
// https://github.com/stack-chan/stackchan-arduino
// https://docs.m5stack.com/en/arduino/stackchan/servo
//
// サーボ: SCS0009（Feetech シリアルバスサーボ）
//   UART Serial2: RX=GPIO7, TX=GPIO6, 1Mbps、M5IOE1（I2C 0x6F）経由
//   X軸（水平）: 0〜360度、中央 160度
//   Y軸（垂直）: 5〜85度、中央 60度（限界角度でロックする恐れがあるため制限）
//
// WiFi 設定: SD カード /config.yaml
//   wifi:
//     ssid: "MySSID"
//     password: "MyPassword"
//
// HTTP API:
//   Port 80: GET /servo?x=<angle>&y=<angle>  サーボ角度指定（どちらか一方でも可）
//            GET /center                      中央に戻す
//   Port 81: GET /stream                      MJPEG ストリーム

#include <M5Unified.h>
#include <SD.h>
#include <WiFi.h>
#include <WebServer.h>
#include <esp_camera.h>
#include <img_converters.h>
#include <gob_GC0308.hpp>
#include <Stackchan_servo.h>

static const int SD_CS_PIN = 4;
static const int X_CENTER  = 160;
static const int Y_CENTER  = 60;
static const int X_MIN     = 0;
static const int X_MAX     = 360;
static const int Y_MIN     = 5;
static const int Y_MAX     = 85;

static WebServer       apiServer(80);
static WiFiServer      streamServer(81);
static StackchanSERVO  servo;
static bool            cameraReady = false;

// --- Config 読み込み ---

static String yamlValue(const String& line) {
    int idx = line.indexOf(':');
    if (idx < 0) return "";
    String val = line.substring(idx + 1);
    val.trim();
    return val;
}

struct Config { String ssid, password; };

static Config loadConfig() {
    Config cfg;
    if (!SD.begin(SD_CS_PIN)) { Serial.println("SD init failed"); return cfg; }
    File file = SD.open("/config.yaml");
    if (!file) { Serial.println("config.yaml not found"); return cfg; }
    String section;
    while (file.available()) {
        String line = file.readStringUntil('\n');
        bool indented = line.startsWith(" ") || line.startsWith("\t");
        line.trim();
        if (line.isEmpty() || line.startsWith("#")) continue;
        if (!indented) {
            section = line.substring(0, line.indexOf(':'));
        } else if (section == "wifi") {
            if (line.indexOf("ssid:")     >= 0) cfg.ssid     = yamlValue(line);
            if (line.indexOf("password:") >= 0) cfg.password = yamlValue(line);
        }
    }
    file.close();
    return cfg;
}

// --- カメラ設定（camera_server と同じピン配置）---

static camera_config_t makeCameraConfig() {
    camera_config_t cfg{};
    cfg.pin_pwdn      = -1;
    cfg.pin_reset     = -1;
    cfg.pin_xclk      = 2;
    cfg.pin_sccb_sda  = -1;
    cfg.pin_sccb_scl  = -1;
    cfg.sccb_i2c_port = M5.In_I2C.getPort();
    cfg.pin_d7 = 47; cfg.pin_d6 = 48;
    cfg.pin_d5 = 16; cfg.pin_d4 = 15;
    cfg.pin_d3 = 42; cfg.pin_d2 = 41;
    cfg.pin_d1 = 40; cfg.pin_d0 = 39;
    cfg.pin_vsync     = 46;
    cfg.pin_href      = 38;
    cfg.pin_pclk      = 45;
    cfg.xclk_freq_hz  = 20000000;
    cfg.ledc_timer    = LEDC_TIMER_0;
    cfg.ledc_channel  = LEDC_CHANNEL_0;
    // GC0308 はハードウェア JPEG 非対応のため RGB565 で取得し、配信時にソフト変換する
    cfg.pixel_format  = PIXFORMAT_RGB565;
    cfg.frame_size    = FRAMESIZE_QVGA;
    cfg.jpeg_quality  = 12;
    cfg.fb_count      = 2;
    cfg.fb_location   = CAMERA_FB_IN_PSRAM;
    cfg.grab_mode     = CAMERA_GRAB_WHEN_EMPTY;
    return cfg;
}

// --- HTTP ハンドラ（サーボ API、Port 80）---

static void handleServo() {
    bool moved = false;
    if (apiServer.hasArg("x")) {
        int angle = constrain(apiServer.arg("x").toInt(), X_MIN, X_MAX);
        servo.moveX(angle, 500);
        moved = true;
    }
    if (apiServer.hasArg("y")) {
        int angle = constrain(apiServer.arg("y").toInt(), Y_MIN, Y_MAX);
        servo.moveY(angle, 500, true);
        moved = true;
    }
    if (!moved) {
        apiServer.send(400, "text/plain", "x or y param required");
        return;
    }
    apiServer.send(200, "text/plain", "ok");
}

static void handleCenter() {
    servo.moveXY(X_CENTER, Y_CENTER, 500);
    apiServer.send(200, "text/plain", "ok");
}

// --- MJPEG ストリームタスク（Core1、Port 81）---
// Core0 の apiServer と分離することでスレッド安全性の問題を回避する

static void streamTask(void*) {
    while (true) {
        WiFiClient client = streamServer.available();
        if (!client) {
            vTaskDelay(10 / portTICK_PERIOD_MS);
            continue;
        }
        // HTTP リクエストヘッダを読み捨てる
        unsigned long timeout = millis() + 2000;
        while (millis() < timeout) {
            if (client.available()) {
                String line = client.readStringUntil('\n');
                if (line == "\r") break;  // 空行 = ヘッダ終端
            }
            vTaskDelay(1 / portTICK_PERIOD_MS);
        }
        client.print(
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: multipart/x-mixed-replace;boundary=frame\r\n\r\n"
        );
        while (client.connected()) {
            camera_fb_t* fb = esp_camera_fb_get();
            if (!fb) break;
            M5.Display.pushImage(0, 0, fb->width, fb->height, (uint16_t*)fb->buf);

            uint8_t* jpg    = nullptr;
            size_t   jpgLen = 0;
            if (frame2jpg(fb, 80, &jpg, &jpgLen)) {
                client.printf(
                    "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %zu\r\n\r\n",
                    jpgLen
                );
                client.write(jpg, jpgLen);
                client.print("\r\n");
                free(jpg);
            }
            esp_camera_fb_return(fb);
        }
    }
}

// --- Setup / Loop ---

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    Serial.begin(115200);
    delay(1000);
    M5.Display.setTextSize(2);
    M5.Display.println("wonder_eye");

    // カメラ初期化
    auto camCfg = makeCameraConfig();
    if (esp_camera_init(&camCfg) != ESP_OK) {
        M5.Display.println("Camera init failed");
        return;
    }
    goblib::camera::GC0308::complementDriver();
    cameraReady = true;

    // サーボ初期化・起動モーション
    servo.begin(7, X_CENTER, 0, 6, Y_CENTER, 0, M5_SCS, &M5.In_I2C);
    delay(500);
    servo.motion(greet);
    servo.moveXY(X_CENTER, Y_CENTER, 500);

    // WiFi 接続
    Config config = loadConfig();
    M5.Display.println("Connecting WiFi...");
    WiFi.begin(config.ssid.c_str(), config.password.c_str());
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > 15000) {
            M5.Display.println("WiFi timeout");
            return;
        }
        delay(500);
    }
    String ip = WiFi.localIP().toString();
    Serial.println("IP: " + ip);
    M5.Display.println(ip);
    M5.Display.println("Servo :80  Stream :81");

    // サーボ API（Port 80）
    apiServer.on("/servo",  HTTP_GET, handleServo);
    apiServer.on("/center", HTTP_GET, handleCenter);
    apiServer.begin();

    // ストリームサーバ（Port 81）→ Core1 タスクで処理
    streamServer.begin();
    xTaskCreatePinnedToCore(streamTask, "stream", 8192, nullptr, 1, nullptr, 1);
}

void loop() {
    M5.update();
    if (!cameraReady) return;
    apiServer.handleClient();
}
