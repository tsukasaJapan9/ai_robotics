import serial

ser = serial.Serial("/dev/ttyUSB0", 115200)

while True:
    line = ser.readline().decode().strip()
    ax, ay, az, gx, gy, gz = map(float, line.split(","))
    print(f"gx={gx}, gy={gy}, gz={gz}, ax={ax}, ay={ay}, az={az}")
