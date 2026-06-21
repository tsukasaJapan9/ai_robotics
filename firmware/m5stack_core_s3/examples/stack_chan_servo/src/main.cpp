// Stack-chan サーボ制御サンプル
// https://github.com/stack-chan/stackchan-arduino
// https://docs.m5stack.com/en/arduino/stackchan/servo
//
// サーボ: SCS0009（Feetech シリアルバスサーボ）
// 通信: UART Serial2（TX=GPIO6, RX=GPIO7, 1Mbps）、M5IOE1(I2C 0x6F)経由
// X軸（水平）: 0〜300度、初期位置 150度
// Y軸（垂直）: 5〜85度推奨、初期位置 90度（端まで動かすと損傷の恐れ）
//
// シリアルコマンド（115200bps）:
//   X<angle>  水平角度を指定（例: X150）
//   Y<angle>  垂直角度を指定（例: Y90）
//   C         中央に戻す
//   G         挨拶モーション

#include <M5Unified.h>
#include "Stackchan_servo.h"

static const int X_CENTER = 150;
static const int Y_CENTER = 90;
static const int X_MIN    = 0;
static const int X_MAX    = 300;
static const int Y_MIN    = 5;   // 端まで動かすと損傷の恐れ
static const int Y_MAX    = 85;

StackchanSERVO servo;

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    M5.Display.setTextSize(2);
    M5.Display.println("Stack-chan Servo");

    servo.begin(6, 7, Y_CENTER, X_CENTER, StackchanSERVO::M5_SCS);
    delay(500);

    // 起動時に挨拶モーション
    servo.motion(StackchanSERVO::Motion::GREET);

    Serial.println("Ready. Commands: X<angle> Y<angle> C G");
}

void loop() {
    M5.update();

    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();

        if (cmd.length() == 0) return;

        char type = cmd.charAt(0);
        int angle = cmd.substring(1).toInt();

        if (type == 'X' || type == 'x') {
            angle = constrain(angle, X_MIN, X_MAX);
            servo.moveX(angle, 500);
            Serial.printf("X -> %d\n", angle);
        } else if (type == 'Y' || type == 'y') {
            angle = constrain(angle, Y_MIN, Y_MAX);
            servo.moveY(angle, 500, true);
            Serial.printf("Y -> %d\n", angle);
        } else if (type == 'C' || type == 'c') {
            servo.moveXY(X_CENTER, Y_CENTER, 500);
            Serial.println("Center");
        } else if (type == 'G' || type == 'g') {
            servo.motion(StackchanSERVO::Motion::GREET);
            Serial.println("Greet");
        } else {
            Serial.println("Unknown command");
        }
    }
}
