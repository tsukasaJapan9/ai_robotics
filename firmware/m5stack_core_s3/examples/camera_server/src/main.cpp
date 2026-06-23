// References:
// https://docs.m5stack.com/en/core/CoreS3
// https://github.com/GOB52/gob_GC0308
// https://github.com/GOB52/M5StackCoreS3_CameraWebServer

#include <M5Unified.h>
#include <SD.h>
#include <WiFi.h>
#include <WebServer.h>
#include <esp_camera.h>
#include <img_converters.h>
#include <gob_GC0308.hpp>

#define SD_CS_PIN 4

struct Config {
    String wifiSsid;
    String wifiPassword;
    String geminiApiKey;
};

static WebServer server(8101);
static bool cameraReady = false;

static String yamlValue(const String& line) {
    int idx = line.indexOf(':');
    if (idx < 0) return "";
    String val = line.substring(idx + 1);
    val.trim();
    return val;
}

static Config loadConfig() {
    Config cfg;
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("SD init failed");
        M5.Lcd.println("SD init failed");
        return cfg;
    }
    Serial.println("SD ok");
    File file = SD.open("/config.yaml");
    if (!file) {
        Serial.println("config.yaml not found");
        M5.Lcd.println("config.yaml not found");
        return cfg;
    }
    Serial.println("config.yaml opened");
    String section;
    while (file.available()) {
        String line = file.readStringUntil('\n');
        bool indented = line.startsWith(" ") || line.startsWith("\t");
        line.trim();
        if (line.isEmpty() || line.startsWith("#")) continue;
        if (!indented) {
            section = line.substring(0, line.indexOf(':'));
        } else if (section == "wifi") {
            if (line.indexOf("ssid:")     >= 0) cfg.wifiSsid     = yamlValue(line);
            if (line.indexOf("password:") >= 0) cfg.wifiPassword = yamlValue(line);
        } else if (section == "gemini") {
            if (line.indexOf("api_key:")  >= 0) cfg.geminiApiKey = yamlValue(line);
        }
    }
    file.close();
    return cfg;
}

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

static void displayFrame(camera_fb_t* fb) {
    M5.Lcd.pushImage(0, 0, fb->width, fb->height, (uint16_t*)fb->buf);
}

static void handleStream() {
    WiFiClient client = server.client();
    client.print(
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=frame\r\n\r\n"
    );
    while (client.connected()) {
        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) break;
        displayFrame(fb);

        // RGB565 → JPEG 変換（GC0308 はハードウェア JPEG 非対応）
        uint8_t* jpg = nullptr;
        size_t jpgLen = 0;
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

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    Serial.begin(115200);
    delay(3000);  // USB CDC 接続待ち
    Serial.println("Boot");

    Config config = loadConfig();
    Serial.println("Config loaded");
    if (config.wifiSsid.isEmpty()) {
        Serial.println("Config load failed");
        return;
    }

    M5.Lcd.println("Connecting to WiFi...");
    WiFi.begin(config.wifiSsid.c_str(), config.wifiPassword.c_str());
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > 15000) {
            Serial.println("WiFi timeout");
            M5.Lcd.println("WiFi timeout");
            return;
        }
        delay(500);
    }
    String ip = WiFi.localIP().toString();
    M5.Lcd.printf("IP: %s\n", ip.c_str());
    Serial.printf("IP: %s\n", ip.c_str());

    auto camCfg = makeCameraConfig();
    if (esp_camera_init(&camCfg) != ESP_OK) {
        M5.Lcd.println("Camera init failed");
        return;
    }
    goblib::camera::GC0308::complementDriver();
    cameraReady = true;
    Serial.println("Camera ready");

    server.on("/stream", handleStream);
    server.begin();
    M5.Lcd.println("Stream: /stream");
    Serial.println("Server started");
}

void loop() {
    M5.update();
    if (!cameraReady) return;
    server.handleClient();

    // handleClient がストリーミング中はブロックするため、
    // ここに到達するのは待機中のみ
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) return;
    displayFrame(fb);
    esp_camera_fb_return(fb);
}
