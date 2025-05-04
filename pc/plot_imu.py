from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial

# シリアル設定
ser = serial.Serial("/dev/ttyUSB0", 115200)  # ポート名は環境に合わせて変更
ser.flush()

# グラフ用のバッファ（最新500点）
max_len = 500
gx_vals = deque([0] * max_len, maxlen=max_len)
gy_vals = deque([0] * max_len, maxlen=max_len)
gz_vals = deque([0] * max_len, maxlen=max_len)

ax_vals = deque([0] * max_len, maxlen=max_len)
ay_vals = deque([0] * max_len, maxlen=max_len)
az_vals = deque([0] * max_len, maxlen=max_len)

angle_vals = deque([0] * max_len, maxlen=max_len)

# プロット設定：3行1列のサブプロット
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# ジャイロ
(line_gx,) = ax1.plot([], [], label="gx")
(line_gy,) = ax1.plot([], [], label="gy")
(line_gz,) = ax1.plot([], [], label="gz")
ax1.set_ylim(-300, 300)
ax1.set_xlim(0, max_len)
ax1.set_title("Gyroscope (deg/sec)")
ax1.legend(loc="upper right")

# 加速度
(line_ax,) = ax2.plot([], [], label="ax")
(line_ay,) = ax2.plot([], [], label="ay")
(line_az,) = ax2.plot([], [], label="az")
ax2.set_ylim(-2, 2)
ax2.set_xlim(0, max_len)
ax2.set_title("Accelerometer (g)")
ax2.legend(loc="upper right")

# 角度
(line_angle,) = ax3.plot([], [], label="angle")
ax3.set_ylim(-180, 180)
ax3.set_xlim(0, max_len)
ax3.set_title("Angle (deg)")
ax3.legend(loc="upper right")

plt.tight_layout()


def update(frame):
    try:
        line = ser.readline().decode().strip()
        gx, gy, gz, ax, ay, az, angle = map(float, line.split(","))
        print(
            f"\rgx={gx:7.3f}, gy={gy:7.3f}, gz={gz:7.3f}, ax={ax:7.3f}, ay={ay:7.3f}, az={az:7.3f}, angle={angle:7.3f}",
            end="",
            flush=True,
        )

        # データ追加
        gx_vals.append(gx)
        gy_vals.append(gy)
        gz_vals.append(gz)
        ax_vals.append(ax)
        ay_vals.append(ay)
        az_vals.append(az)
        angle_vals.append(angle)

        # グラフ更新
        line_gx.set_data(range(len(gx_vals)), gx_vals)
        line_gy.set_data(range(len(gy_vals)), gy_vals)
        line_gz.set_data(range(len(gz_vals)), gz_vals)

        line_ax.set_data(range(len(ax_vals)), ax_vals)
        line_ay.set_data(range(len(ay_vals)), ay_vals)
        line_az.set_data(range(len(az_vals)), az_vals)

        line_angle.set_data(range(len(angle_vals)), angle_vals)

    except Exception as e:
        print(f"\nError: {e}")

    return line_gx, line_gy, line_gz, line_ax, line_ay, line_az, line_angle


ani = animation.FuncAnimation(fig, update, interval=1, blit=True)
plt.show()
