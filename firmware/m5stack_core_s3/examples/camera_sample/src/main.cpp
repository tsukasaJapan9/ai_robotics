// References:
// https://docs.m5stack.com/en/core/CoreS3
// https://github.com/GOB52/gob_GC0308
// https://github.com/GOB52/M5StackCoreS3_CameraWebServer

#include <M5Unified.h>
#include <esp_camera.h>
#include <gob_GC0308.hpp>

static camera_config_t makeCameraConfig() {
    camera_config_t cfg{};
    cfg.pin_pwdn     = -1;
    cfg.pin_reset    = -1;
    cfg.pin_xclk     = 2;
    cfg.pin_sccb_sda    = -1;  // M5Unified が初期化済みの I2C バスを使う
    cfg.pin_sccb_scl    = -1;
    cfg.sccb_i2c_port   = M5.In_I2C.getPort();
    cfg.pin_d7 = 47; cfg.pin_d6 = 48;
    cfg.pin_d5 = 16; cfg.pin_d4 = 15;
    cfg.pin_d3 = 42; cfg.pin_d2 = 41;
    cfg.pin_d1 = 40; cfg.pin_d0 = 39;
    cfg.pin_vsync    = 46;
    cfg.pin_href     = 38;
    cfg.pin_pclk     = 45;
    cfg.xclk_freq_hz = 20000000;
    cfg.ledc_timer   = LEDC_TIMER_0;
    cfg.ledc_channel = LEDC_CHANNEL_0;
    cfg.pixel_format = PIXFORMAT_RGB565;
    cfg.frame_size   = FRAMESIZE_QVGA;
    cfg.fb_count     = 2;
    cfg.fb_location  = CAMERA_FB_IN_PSRAM;
    cfg.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
    return cfg;
}

static bool cameraReady = false;

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    Serial.begin(115200);

    while (!Serial && millis() < 3000);  // USB CDC 接続待ち（最大3秒）

    M5.Lcd.print("Initializing camera...");

    auto camCfg = makeCameraConfig();
    if (esp_camera_init(&camCfg) != ESP_OK) {
        Serial.println("Camera init failed");
        M5.Lcd.println("\nCamera init failed");
        return;
    }
    goblib::camera::GC0308::complementDriver();
    Serial.println("Camera ready");
    M5.Lcd.println("\nCamera ready");
    cameraReady = true;
}

void loop() {
    M5.update();
    if (!cameraReady) return;

    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Frame capture failed");
        return;
    }

    M5.Lcd.pushImage(0, 0, fb->width, fb->height, (uint16_t*)fb->buf);
    esp_camera_fb_return(fb);
}
