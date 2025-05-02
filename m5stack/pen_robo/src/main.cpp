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

  if (M5.BtnC.wasPressed())
  {
    controlEnable = !controlEnable;
    if (controlEnable)
    {
      control_torque(true);
    }
    else
    {
      control_torque(false);
    }
  }

  float gx, gy, gz;
  float ax, ay, az;

  M5.Imu.getGyro(&gx, &gy, &gz);
  M5.Imu.getAccel(&ax, &ay, &az);

  // PCに送信
  Serial.printf("%7.3f,%7.3f,%7.3f,%7.3f,%7.3f,%7.3f\n", gx, gy, gz, ax, ay, az);

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
  M5.Lcd.fillRect(prevBallX - BALL_RADIUS, prevBallY - BALL_RADIUS, BALL_RADIUS * 2 + 1, BALL_RADIUS * 2 + 1, BLACK);
  int ballColor = RED;
  if (controlEnable)
  {
    ballColor = GREEN;
  }
  M5.Lcd.fillCircle((int)ballX, (int)ballY, BALL_RADIUS, ballColor);

  prevBallX = ballX;
  prevBallY = ballY;

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

  // 制御モードでない場合はここで終わり
  if (!controlEnable)
  {
    return;
  }

  dxl.setGoalPosition(RIGHT_LEG_ID, 205, UNIT_DEGREE);
  dxl.setGoalPosition(LEFT_LEG_ID, 205, UNIT_DEGREE);
  delay(1000);

  // Set Goal Velocity using RPM
  dxl.setGoalVelocity(RIGHT_WHL_ID, 60, UNIT_RPM);
  dxl.setGoalVelocity(LEFT_WHL_ID, 60, UNIT_RPM);
  delay(1000);

  dxl.setGoalPosition(RIGHT_LEG_ID, 245, UNIT_DEGREE);
  dxl.setGoalPosition(LEFT_LEG_ID, 245, UNIT_DEGREE);
  delay(1000);

  dxl.setGoalVelocity(RIGHT_WHL_ID, -60, UNIT_RPM);
  dxl.setGoalVelocity(LEFT_WHL_ID, -60, UNIT_RPM);
  delay(1000);
}
