from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial

GYRO = False

# シリアル設定
ser = serial.Serial("/dev/ttyUSB0", 115200)  # ポート名は環境に合わせて変更
ser.flush()

# グラフ用のバッファ（最新100点）
max_len = 500
gx_vals = deque([0] * max_len, maxlen=max_len)
gy_vals = deque([0] * max_len, maxlen=max_len)
gz_vals = deque([0] * max_len, maxlen=max_len)

ax_vals = deque([0] * max_len, maxlen=max_len)
ay_vals = deque([0] * max_len, maxlen=max_len)
az_vals = deque([0] * max_len, maxlen=max_len)

# プロット初期設定
fig, ax = plt.subplots()
if GYRO:
    (line_x,) = ax.plot([], [], label="gx")
    (line_y,) = ax.plot([], [], label="gy")
    (line_z,) = ax.plot([], [], label="gz")
else:
    (line_x,) = ax.plot([], [], label="ax")
    (line_y,) = ax.plot([], [], label="ay")
    (line_z,) = ax.plot([], [], label="az")

if GYRO:
    ax.set_ylim(-300, 300)  # 単位は deg/sec
else:
    ax.set_ylim(-2, 2)  # 単位はg

ax.set_xlim(0, max_len)
ax.set_title("Real-time Gyro Data")
ax.legend()


def update_gyro(frame):
    try:
        line = ser.readline().decode().strip()
        gx, gy, gz, ax, ay, az = map(float, line.split(","))
        print(
            f"\rgx={gx:7.3f}, gy={gy:7.3f}, gz={gz:7.3f}, ax={ax:7.3f}, ay={ay:7.3f}, az={az:7.3f}",
            end="",
            flush=True,
        )

        gx_vals.append(gx)
        gy_vals.append(gy)
        gz_vals.append(gz)

        line_x.set_data(range(len(gx_vals)), gx_vals)
        line_y.set_data(range(len(gy_vals)), gy_vals)
        line_z.set_data(range(len(gz_vals)), gz_vals)

    except Exception as e:
        print(f"Error: {e}")

    return line_x, line_y, line_z


def update_accel(frame):
    try:
        line = ser.readline().decode().strip()
        gx, gy, gz, ax, ay, az = map(float, line.split(","))
        print(
            f"\rgx={gx:7.3f}, gy={gy:7.3f}, gz={gz:7.3f}, ax={ax:7.3f}, ay={ay:7.3f}, az={az:7.3f}",
            end="",
            flush=True,
        )
        ax_vals.append(ax)
        ay_vals.append(ay)
        az_vals.append(az)

        line_x.set_data(range(len(ax_vals)), ax_vals)
        line_y.set_data(range(len(ay_vals)), ay_vals)
        line_z.set_data(range(len(az_vals)), az_vals)

    except Exception as e:
        print(f"Error: {e}")

    return line_x, line_y, line_z


if GYRO:
    ani = animation.FuncAnimation(fig, update_gyro, interval=1, blit=True)
else:
    ani = animation.FuncAnimation(fig, update_accel, interval=1, blit=True)

plt.show()
