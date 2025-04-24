from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial

# シリアル設定
ser = serial.Serial("/dev/ttyUSB0", 115200)  # ポート名は環境に合わせて変更
ser.flush()

# グラフ用のバッファ（最新100点）
max_len = 500
gx_vals = deque([0] * max_len, maxlen=max_len)
gy_vals = deque([0] * max_len, maxlen=max_len)
gz_vals = deque([0] * max_len, maxlen=max_len)

# プロット初期設定
fig, ax = plt.subplots()
(line_gx,) = ax.plot([], [], label="gx")
(line_gy,) = ax.plot([], [], label="gy")
(line_gz,) = ax.plot([], [], label="gz")
ax.set_ylim(-2.5, 2.5)  # 単位は deg/sec
ax.set_xlim(0, max_len)
ax.set_title("Real-time Gyro Data")
ax.legend()


def update(frame):
    try:
        line = ser.readline().decode().strip()
        ax, ay, az, gx, gy, gz = map(float, line.split(","))
        # print(f"gx={gx}, gy={gy}, gz={gz}, ax={ax}, ay={ay}, az={az}")

        gx_vals.append(gx)
        gy_vals.append(gy)
        gz_vals.append(gz)

        line_gx.set_data(range(len(gx_vals)), gx_vals)
        line_gy.set_data(range(len(gy_vals)), gy_vals)
        line_gz.set_data(range(len(gz_vals)), gz_vals)

    except Exception as e:
        print(f"Error: {e}")

    return line_gx, line_gy, line_gz


ani = animation.FuncAnimation(fig, update, interval=1, blit=True)
plt.show()
