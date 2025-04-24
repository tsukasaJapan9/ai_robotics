#include <M5Atom.h>
#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel pixels(64, 26, NEO_GRB + NEO_KHZ800);

#define DATA_SIZE 192
#define MATRIX_SIZE 64
uint8_t rgb_data[DATA_SIZE];

void setup()
{
  M5.begin(true, false, false);
  Serial.begin(115200);
  while (!Serial)
    ;
  Serial.println("Ready to receive RGB data");
  pixels.begin();

  // 消灯
  for (int i = 0; i < MATRIX_SIZE; i++)
  {
    int r = 0;
    int g = 0;
    int b = 0;
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
  pixels.show();
}

void loop()
{
  // PCからのシリアル通信のデータを受信
  if (Serial.available() >= DATA_SIZE)
  {
    Serial.readBytes(rgb_data, DATA_SIZE);

    for (int i = 0; i < DATA_SIZE; i += 3)
    {
      int r = rgb_data[i + 0];
      int g = rgb_data[i + 1];
      int b = rgb_data[i + 2];
      int led_id = int(i / 3);
      pixels.setPixelColor(led_id, pixels.Color(r, g, b));
    }
    pixels.show();
  }
}
