import serial

LED_MAX_BRIGHTNESS = 32
ser = serial.Serial("/dev/ttyUSB0", 115200)

# 送信するRGBデータ
rgb_data: list[int] = []
for i in range(64):
    r = 10
    g = 0
    b = 0
    rgb_data.extend([r, g, b])

ser.write(bytearray(rgb_data))
ser.close()
