import serial

ser = serial.Serial("/dev/ttyUSB0", 115200)

while True:
    line = ser.readline().decode().strip()
    gx, gy, gz, ax, ay, az = list(map(float, line.split(",")))
    print(
        f"\rgx={gx:7.3f}, gy={gy:7.3f}, gz={gz:7.3f}, ax={ax:7.3f}, ay={ay:7.3f}, az={az:7.3f}",
        end="",
        flush=True,
    )
