import serial

LED_MAX_BRIGHTNESS = 32
BRIGHTNESS_DIVIDER = 2
ser = serial.Serial("/dev/ttyUSB0", 115200)

# 送信するRGBデータ
rgb_data: list[int] = []
for i in range(64):
    r = 0
    g = i * 2
    b = i * 2
    r = int(r // BRIGHTNESS_DIVIDER)
    g = int(g // BRIGHTNESS_DIVIDER)
    b = int(b // BRIGHTNESS_DIVIDER)
    rgb_data.extend([r, g, b])

ser.write(bytearray(rgb_data))
ser.close()
