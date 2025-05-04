#include <Dynamixel2Arduino.h>
#include <M5Unified.h>

// ボール描画用
#define MAX_DISP_X 320
#define MAX_DISP_Y 240
#define BALL_RADIUS 30

float ballX = MAX_DISP_X / 2; // ボールのX位置（中央からスタート）
float ballY = MAX_DISP_Y / 2; // ボールのY位置（文字表示より下）
float prevBallX = ballX;
float prevBallY = ballY;

// サーボモータ制御用
HardwareSerial &DXL_SERIAL = Serial1;
Dynamixel2Arduino dxl;

// M5Stack Core2 PORT A
const uint8_t RX_SERVO = 33;
const uint8_t TX_SERVO = 32;

const uint8_t RIGHT_LEG_ID = 2;
const uint8_t RIGHT_WHL_ID = 3;
const uint8_t LEFT_LEG_ID = 1;
const uint8_t LEFT_WHL_ID = 4;

const float DXL_PROTOCOL_VERSION = 2.0;

using namespace ControlTableItem;

bool controlEnable = false;

// 制御パラメータ(要調整)
#define MAX_RPM 120.0
float Kp = 200.0, Ki = 0.0, Kd = 200;
float scale = 0.1;

float last_error;
float integral = 0;

bool is_first = true;
float target_angle = 0;

// 処理時間計測
float prev_time = millis();

void control_torque(bool enable)
{
  if (enable)
  {
    dxl.torqueOn(RIGHT_LEG_ID);
    dxl.torqueOn(RIGHT_WHL_ID);
    dxl.torqueOn(LEFT_LEG_ID);
    dxl.torqueOn(LEFT_WHL_ID);
  }
  else
  {

    dxl.torqueOff(RIGHT_LEG_ID);
    dxl.torqueOff(RIGHT_WHL_ID);
    dxl.torqueOff(LEFT_LEG_ID);
    dxl.torqueOff(LEFT_WHL_ID);
  }
}

void setup()
{
  auto cfg = M5.config();
  M5.begin(cfg);
  M5.Imu.begin();
  Serial.begin(115200); // PCとの通信速度

  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(WHITE, BLACK);

  // ================================
  // サーボの初期化
  // ================================
  DXL_SERIAL.begin(1000000, SERIAL_8N1, RX_SERVO, TX_SERVO);
  dxl = Dynamixel2Arduino(DXL_SERIAL);

  dxl.begin(1000000);
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  dxl.ping(RIGHT_LEG_ID);
  dxl.ping(RIGHT_WHL_ID);
  dxl.ping(LEFT_LEG_ID);
  dxl.ping(LEFT_WHL_ID);

  control_torque(false);

  dxl.setOperatingMode(RIGHT_LEG_ID, OP_POSITION);
  dxl.setOperatingMode(LEFT_LEG_ID, OP_POSITION);

  dxl.setOperatingMode(RIGHT_WHL_ID, OP_VELOCITY);
  dxl.setOperatingMode(LEFT_WHL_ID, OP_VELOCITY);
}

void loop()
{
  M5.update();

  float gx, gy, gz;
  float ax, ay, az;

  M5.Imu.getGyro(&gx, &gy, &gz);
  M5.Imu.getAccel(&ax, &ay, &az);

  // 姿勢(直立時にゼロ、前方向に倒れた時にプラス、後ろ方向に倒れた時にマイナス)
  float angle = atan2(ay, az) * 180 / PI;

  if (M5.BtnC.wasPressed())
  {
    controlEnable = !controlEnable;
    if (controlEnable)
    {
      control_torque(true);
      dxl.setGoalPosition(RIGHT_LEG_ID, 205, UNIT_DEGREE);
      dxl.setGoalPosition(LEFT_LEG_ID, 205, UNIT_DEGREE);
      target_angle = angle;
      M5.Lcd.setTextColor(WHITE, DARKGREY);
    }
    else
    {
      control_torque(false);
      M5.Lcd.setTextColor(WHITE, BLACK);
    }
  }

  // PCに送信
  Serial.printf("%7.3f,%7.3f,%7.3f,%7.3f,%7.3f,%7.3f, %7.3f\n", gx, gy, gz, ax, ay, az, angle);

  // --- ボールの位置更新（gyに応じて左右移動） ---
  float scale = 0.1;
  float velocityX = gy * scale;
  float velocityY = gx * scale;
  ballX += velocityX;
  ballY += velocityY;

  if (ballX < 0)
    ballX = 0;
  if (ballX >= MAX_DISP_X)
    ballX = MAX_DISP_X - 1;

  if (ballY < 0)
    ballY = 0;
  if (ballY >= MAX_DISP_Y)
    ballY = MAX_DISP_Y - 1;

  // 1フレーム前のボールを消去する
  // M5.Lcd.fillRect(prevBallX - BALL_RADIUS, prevBallY - BALL_RADIUS, BALL_RADIUS * 2 + 1, BALL_RADIUS * 2 + 1, BLACK);
  // int ballColor = RED;
  // if (controlEnable)
  // {
  //   ballColor = GREEN;
  // }
  // M5.Lcd.fillCircle((int)ballX, (int)ballY, BALL_RADIUS, ballColor);

  // prevBallX = ballX;
  // prevBallY = ballY;

  if (!controlEnable)
  {
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.printf("gx: %7.3f dps\n", gx);
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.printf("gy: %7.3f dps\n", gy);
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.printf("gz: %7.3f dps\n", gz);

    M5.Lcd.setCursor(10, 70);
    M5.Lcd.printf("ax: %7.3f g\n", ax);
    M5.Lcd.setCursor(10, 90);
    M5.Lcd.printf("ay: %7.3f g\n", ay);
    M5.Lcd.setCursor(10, 110);
    M5.Lcd.printf("az: %7.3f g\n", az);

    M5.Lcd.setCursor(10, 130);
    M5.Lcd.printf("angle: %7.3f deg\n", angle);
  }

  // 目標確度からの差分
  float error = target_angle - angle;
  // 前回のエラーとの差
  float derivative = error - last_error;
  // 差分の積算値
  integral += error;
  // outは目標値に近いほど0になり、前に倒れるとマイナス、後ろに倒れるとプラスになる
  float output = Kp * error + Ki * integral + Kd * derivative;
  last_error = error;

  M5.Lcd.setCursor(10, 150);
  M5.Lcd.printf("out: %7.3f deg\n", output);

  output *= scale;
  if (output > MAX_RPM)
    output = MAX_RPM;
  if (output < -MAX_RPM)
    output = -MAX_RPM;

  M5.Lcd.setCursor(10, 170);
  M5.Lcd.printf("ctrl: %7.3f deg\n", output);

  // 制御モードのときだけサーボを動かす
  if (controlEnable)
  {
    dxl.setGoalVelocity(RIGHT_WHL_ID, output, UNIT_RPM);
    dxl.setGoalVelocity(LEFT_WHL_ID, output, UNIT_RPM);
  }

  float now_time = millis();

  M5.Lcd.setCursor(10, 190);
  M5.Lcd.printf("interval: %7.3f ms\n", now_time - prev_time);

  prev_time = now_time;

  // テストモード
  // dxl.setGoalPosition(RIGHT_LEG_ID, 205, UNIT_DEGREE);
  // dxl.setGoalPosition(LEFT_LEG_ID, 205, UNIT_DEGREE);
  // delay(1000);

  // // Set Goal Velocity using RPM
  // dxl.setGoalVelocity(RIGHT_WHL_ID, 60, UNIT_RPM);
  // dxl.setGoalVelocity(LEFT_WHL_ID, 60, UNIT_RPM);
  // delay(1000);

  // dxl.setGoalPosition(RIGHT_LEG_ID, 245, UNIT_DEGREE);
  // dxl.setGoalPosition(LEFT_LEG_ID, 245, UNIT_DEGREE);
  // delay(1000);

  // dxl.setGoalVelocity(RIGHT_WHL_ID, -60, UNIT_RPM);
  // dxl.setGoalVelocity(LEFT_WHL_ID, -60, UNIT_RPM);
  // delay(1000);
}
