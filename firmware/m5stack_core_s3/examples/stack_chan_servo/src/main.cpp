// Stack-chan サーボ HTTP 制御
// https://github.com/stack-chan/stackchan-arduino
// https://docs.m5stack.com/en/arduino/stackchan/servo
//
// サーボ: SCS0009（Feetech シリアルバスサーボ）
// 通信: UART Serial2（RX=GPIO7, TX=GPIO6, 1Mbps）、M5IOE1(I2C 0x6F)経由
// X軸（水平）: 0〜360度、初期位置 160度（角度制限不要）
// Y軸（垂直）: 5〜85度推奨、初期位置 90度
//   限界角度で動作させるとサーボがロックし故障する恐れがあるため制限する
//
// WiFi 設定: SD カード /config.yaml
//   wifi:
//     ssid: "MySSID"
//     password: "MyPassword"
//
// HTTP API:
//   GET /servo?x=<angle>&y=<angle>  X・Y 軸を指定（どちらか一方でも可）
//   GET /center                     中央に戻す

#include <M5Unified.h>
#include <Stackchan_servo.h>
#include <WiFi.h>
#include <WebServer.h>
#include <SD.h>

static const int SD_CS_PIN = 4;
static const int X_CENTER  = 160;
static const int Y_CENTER  = 45;
static const int X_MIN     = 0;    // 物理的な可動範囲
static const int X_MAX     = 360;
static const int Y_MIN     = 5;    // 故障防止のため限界角度を避ける
static const int Y_MAX     = 85;

StackchanSERVO servo;
WebServer server(80);

// --- config.yaml 読み込み ---

static String yamlValue(const String& line) {
    int idx = line.indexOf(':');
    if (idx < 0) return "";
    String val = line.substring(idx + 1);
    val.trim();
    return val;
}

struct Config {
    String ssid;
    String password;
};

static Config loadConfig() {
    Config cfg;
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("SD init failed");
        return cfg;
    }
    File file = SD.open("/config.yaml");
    if (!file) {
        Serial.println("config.yaml not found");
        return cfg;
    }
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

// --- HTTP ハンドラ ---

static void handleServo() {
    bool moved = false;
    if (server.hasArg("x")) {
        int angle = constrain(server.arg("x").toInt(), X_MIN, X_MAX);
        servo.moveX(angle, 500);
        moved = true;
    }
    if (server.hasArg("y")) {
        int angle = constrain(server.arg("y").toInt(), Y_MIN, Y_MAX);
        servo.moveY(angle, 500, true);
        moved = true;
    }
    if (!moved) {
        server.send(400, "text/plain", "x or y param required");
        return;
    }
    server.send(200, "text/plain", "ok");
}

static void handleCenter() {
    servo.moveXY(X_CENTER, Y_CENTER, 500);
    server.send(200, "text/plain", "ok");
}

// --- setup / loop ---

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    M5.Display.setTextSize(2);
    M5.Display.println("Stack-chan");

    servo.begin(7, X_CENTER, 0, 6, Y_CENTER, 0, M5_SCS, &M5.In_I2C);
    delay(500);
    servo.motion(greet);
    servo.moveXY(X_CENTER, Y_CENTER, 500);

    // WiFi 接続
    Config config = loadConfig();
    M5.Display.println("Connecting WiFi...");
    WiFi.begin(config.ssid.c_str(), config.password.c_str());
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    String ip = WiFi.localIP().toString();
    Serial.println("IP: " + ip);
    M5.Display.println(ip);

    // HTTP サーバ
    server.on("/servo",  HTTP_GET, handleServo);
    server.on("/center", HTTP_GET, handleCenter);
    server.begin();
    Serial.println("HTTP server started");
}

void loop() {
    M5.update();
    server.handleClient();
}
