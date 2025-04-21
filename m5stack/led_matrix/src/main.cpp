#include <M5Atom.h>
#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel pixels(64, 26, NEO_GRB + NEO_KHZ800);

#define DATA_SIZE 192
#define MATRIX_SIZE 64
uint8_t rgb_data[DATA_SIZE];

CRGB dispColor(uint8_t r, uint8_t g, uint8_t b)
{
  return (CRGB)((r << 16) | (g << 8) | b);
}

void setup()
{
  M5.begin(true, false, false);
  Serial.begin(115200);
  // while (!Serial)
  //   ;
  Serial.println("Ready to receive RGB data");
  pixels.begin();

  // M5.dis.drawpix(0, dispColor(0, 0, 0));

  // 消灯
  for (int i = 0; i < MATRIX_SIZE; i += 3)
  {
    int r = 0;
    int g = 0;
    int b = 0;
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
  pixels.show();
}

// size_t readBytes(uint8_t *buffer, size_t length);
void loop()
{
  M5.update();  //本体のボタン状態更新
  bool flag = false;
  if (M5.Btn.isPressed())
  { // ボタンが押されていれば
    // M5.dis.drawpix(0, dispColor(0, 0, 255)); //LED（指定色）
    flag = false;
  }
  else
  { // ボタンが押されてなければ
    flag = true;
    // M5.dis.drawpix(0, dispColor(20, 20, 20));    //LED（白）
  }
  delay(100); // 100ms待機
  // M5.dis.drawpix(0, dispColor(255, 0, 0));

  // // PCからのシリアル通信のデータを受信
  // if (Serial.available() > DATA_SIZE)
  // {
  //   Serial.readBytes(rgb_data, DATA_SIZE);

  //   // Serial.print("First RGB: ");
  //   // Serial.print(rgb_data[0]);
  //   // Serial.print(", ");
  //   // Serial.print(rgb_data[1]);
  //   // Serial.print(", ");
  //   // Serial.println(rgb_data[2]);

  //   for (int i = 0; i < MATRIX_SIZE; i += 3)
  //   {
  //     int r = rgb_data[i + 0];
  //     int g = rgb_data[i + 1];
  //     int b = rgb_data[i + 2];
  //     pixels.setPixelColor(i, pixels.Color(r, g, b));
  //   }
  //   pixels.show();
  // }
  for (int i = 0; i < MATRIX_SIZE; i++)
  {
    int r = 0;
    int g = 0;
    int b = 0;
    if (flag) {
      r = i;
    } else {
      g = i;
    }
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
  pixels.show();
}
