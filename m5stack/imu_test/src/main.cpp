#include <M5Unified.h>

#define MAX_DISP_X 320
#define MAX_DISP_Y 240
#define BALL_RADIUS 30

float ballX = MAX_DISP_X / 2; // ボールのX位置（中央からスタート）
float ballY = MAX_DISP_Y / 2; // ボールのY位置（文字表示より下）
float prevBallX = ballX;
float prevBallY = ballY;

void setup()
{
  auto cfg = M5.config();
  M5.begin(cfg);
  M5.Imu.begin();
  Serial.begin(115200); // PCとの通信速度

  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(WHITE, BLACK);
}

void loop()
{
  M5.update();

  float gx, gy, gz;
  float ax, ay, az;

  M5.Imu.getGyro(&gx, &gy, &gz);
  M5.Imu.getAccel(&ax, &ay, &az);

  // PCに送信
  Serial.printf("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n", gx, gy, gz, ax, ay, az);

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

  M5.Lcd.fillCircle((int)ballX, (int)ballY, BALL_RADIUS, RED);

  prevBallX = ballX;
  prevBallY = ballY;

  M5.Lcd.setCursor(10, 10);
  M5.Lcd.printf("gx: %6.2f dps\n", gx);
  M5.Lcd.setCursor(10, 30);
  M5.Lcd.printf("gy: %6.2f dps\n", gy);
  M5.Lcd.setCursor(10, 50);
  M5.Lcd.printf("gz: %6.2f dps\n", gz);

  if (M5.BtnC.wasPressed())
  {
    ballX = MAX_DISP_X / 2;
    ballY = MAX_DISP_Y / 2;
    prevBallX = ballX;
    prevBallY = ballY;
  }
}
