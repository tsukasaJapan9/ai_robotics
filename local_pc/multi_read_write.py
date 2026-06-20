############################################
# 複数のサーボに司令を送ったり現在値を取得するテスト
# ロボットに組み付けた状態で実行しないこと
############################################
import time

from servo import (
    create_hander,
    get_drive_mode,
    get_operating_mode,
    get_position,
    get_velocity,
    set_drive_mode,
    set_operating_mode,
    set_position,
    set_torque,
    set_velocity,
)

CMD_NORMAL_MODE = 0x00
CMD_REVERSE_MODE = 0x01
CMD_VELOCITY_CONTROL_MODE = 0x01
CMD_POSITION_CONTROL_MODE = 0x03

RIGHT_LEG_ID = 2
LEFT_LEG_ID = 1
RIGHT_WHEEL_ID = 3
LEFT_WHEEL_ID = 4


def main() -> None:
    port_handler, packet_handler = create_hander()
    if port_handler is None or packet_handler is None:
        return

    # 制御モードを変更
    set_operating_mode(
        port_handler, packet_handler, RIGHT_LEG_ID, CMD_POSITION_CONTROL_MODE
    )
    set_operating_mode(
        port_handler, packet_handler, LEFT_LEG_ID, CMD_POSITION_CONTROL_MODE
    )
    set_operating_mode(
        port_handler, packet_handler, RIGHT_WHEEL_ID, CMD_VELOCITY_CONTROL_MODE
    )
    set_operating_mode(
        port_handler, packet_handler, LEFT_WHEEL_ID, CMD_VELOCITY_CONTROL_MODE
    )

    time.sleep(1)

    _, val = get_operating_mode(port_handler, packet_handler, RIGHT_LEG_ID)
    print(f"ID: {RIGHT_LEG_ID}, operating mode: {val}")
    _, val = get_operating_mode(port_handler, packet_handler, LEFT_LEG_ID)
    print(f"ID: {LEFT_LEG_ID}, operating mode: {val}")
    _, val = get_operating_mode(port_handler, packet_handler, RIGHT_WHEEL_ID)
    print(f"ID: {RIGHT_WHEEL_ID}, operating mode: {val}")
    _, val = get_operating_mode(port_handler, packet_handler, LEFT_WHEEL_ID)
    print(f"ID: {LEFT_WHEEL_ID}, operating mode: {val}")

    # リバースモードを設定
    set_drive_mode(port_handler, packet_handler, RIGHT_LEG_ID, CMD_NORMAL_MODE)
    set_drive_mode(port_handler, packet_handler, LEFT_LEG_ID, CMD_REVERSE_MODE)
    set_drive_mode(port_handler, packet_handler, RIGHT_WHEEL_ID, CMD_NORMAL_MODE)
    set_drive_mode(port_handler, packet_handler, LEFT_WHEEL_ID, CMD_REVERSE_MODE)

    time.sleep(1)

    _, val = get_drive_mode(port_handler, packet_handler, RIGHT_LEG_ID)
    print(f"ID: {RIGHT_LEG_ID}, drive mode: {val}")
    _, val = get_drive_mode(port_handler, packet_handler, LEFT_LEG_ID)
    print(f"ID: {LEFT_LEG_ID}, drive mode: {val}")
    _, val = get_drive_mode(port_handler, packet_handler, RIGHT_WHEEL_ID)
    print(f"ID: {RIGHT_WHEEL_ID}, drive mode: {val}")
    _, val = get_drive_mode(port_handler, packet_handler, LEFT_WHEEL_ID)
    print(f"ID: {LEFT_WHEEL_ID}, drive mode: {val}")

    # トルクを入れる
    set_torque(port_handler, packet_handler, RIGHT_LEG_ID, True)
    set_torque(port_handler, packet_handler, LEFT_LEG_ID, True)
    set_torque(port_handler, packet_handler, RIGHT_WHEEL_ID, True)
    set_torque(port_handler, packet_handler, LEFT_WHEEL_ID, True)

    set_position(port_handler, packet_handler, RIGHT_LEG_ID, 0)
    set_position(port_handler, packet_handler, LEFT_LEG_ID, 0)
    time.sleep(1)
    for i in range(361):
        set_position(port_handler, packet_handler, RIGHT_LEG_ID, i)
        set_position(port_handler, packet_handler, LEFT_LEG_ID, i)
        _, pos = get_position(port_handler, packet_handler, RIGHT_LEG_ID)
        print(f"ID: {RIGHT_LEG_ID}, position: {pos}")
        _, pos = get_position(port_handler, packet_handler, LEFT_LEG_ID)
        print(f"ID: {LEFT_LEG_ID}, position: {pos}")

    time.sleep(1)
    _, pos = get_position(port_handler, packet_handler, RIGHT_LEG_ID)
    print(f"ID: {RIGHT_LEG_ID}, position: {pos}")
    _, pos = get_position(port_handler, packet_handler, LEFT_LEG_ID)
    print(f"ID: {LEFT_LEG_ID}, position: {pos}")

    set_velocity(port_handler, packet_handler, RIGHT_WHEEL_ID, 60)
    set_velocity(port_handler, packet_handler, LEFT_WHEEL_ID, 60)

    time.sleep(3)

    _, vel = get_velocity(port_handler, packet_handler, RIGHT_WHEEL_ID)
    print(f"ID: {RIGHT_WHEEL_ID}, velocity: {vel}")
    _, vel = get_velocity(port_handler, packet_handler, LEFT_WHEEL_ID)
    print(f"ID: {LEFT_WHEEL_ID}, velocity: {vel}")

    set_velocity(port_handler, packet_handler, RIGHT_WHEEL_ID, -60)
    set_velocity(port_handler, packet_handler, LEFT_WHEEL_ID, -60)

    time.sleep(3)

    _, vel = get_velocity(port_handler, packet_handler, RIGHT_WHEEL_ID)
    print(f"ID: {RIGHT_WHEEL_ID}, velocity: {vel}")
    _, vel = get_velocity(port_handler, packet_handler, LEFT_WHEEL_ID)
    print(f"ID: {LEFT_WHEEL_ID}, velocity: {vel}")

    # トルクを抜く
    set_torque(port_handler, packet_handler, RIGHT_LEG_ID, False)
    set_torque(port_handler, packet_handler, LEFT_LEG_ID, False)
    set_torque(port_handler, packet_handler, RIGHT_WHEEL_ID, False)
    set_torque(port_handler, packet_handler, LEFT_WHEEL_ID, False)


if __name__ == "__main__":
    main()
