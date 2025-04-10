import time

from servo import (
    create_hander,
    get_drive_mode,
    get_operating_mode,
    set_drive_mode,
    set_operating_mode,
    set_position,
    set_torque,
)

CMD_NORMAL_MODE = 0x00
CMD_REVERSE_MODE = 0x01
CMD_VELOCITY_CONTROL_MODE = 0x01
CMD_POSITION_CONTROL_MODE = 0x03

RIGHT_LEG_ID = 1
LEFT_LEG_ID = 2
RIGHT_WHEEL_ID = 4
LEFT_WHEEL_ID = 3


def main() -> None:
    port_handler, packet_handler = create_hander()
    if port_handler is None or packet_handler is None:
        return

    # トルクを抜く
    set_torque(port_handler, packet_handler, RIGHT_LEG_ID, False)
    set_torque(port_handler, packet_handler, LEFT_LEG_ID, False)
    set_torque(port_handler, packet_handler, RIGHT_WHEEL_ID, False)
    set_torque(port_handler, packet_handler, LEFT_WHEEL_ID, False)
    time.sleep(1)

    # 制御モードを変更
    set_operating_mode(
        port_handler, packet_handler, RIGHT_LEG_ID, CMD_POSITION_CONTROL_MODE
    )
    set_operating_mode(
        port_handler, packet_handler, LEFT_LEG_ID, CMD_POSITION_CONTROL_MODE
    )
    set_operating_mode(
        port_handler, packet_handler, RIGHT_WHEEL_ID, CMD_POSITION_CONTROL_MODE
    )
    set_operating_mode(
        port_handler, packet_handler, LEFT_WHEEL_ID, CMD_POSITION_CONTROL_MODE
    )

    time.sleep(2)

    # 制御モードを取得して表示
    _, val = get_operating_mode(port_handler, packet_handler, RIGHT_LEG_ID)
    print(f"ID: {RIGHT_LEG_ID}, operating mode: {val}")
    _, val = get_operating_mode(port_handler, packet_handler, LEFT_LEG_ID)
    print(f"ID: {LEFT_LEG_ID}, operating mode: {val}")
    _, val = get_operating_mode(port_handler, packet_handler, RIGHT_WHEEL_ID)
    print(f"ID: {RIGHT_WHEEL_ID}, operating mode: {val}")
    _, val = get_operating_mode(port_handler, packet_handler, LEFT_WHEEL_ID)
    print(f"ID: {LEFT_WHEEL_ID}, operating mode: {val}")

    # ドライブモードを設定
    set_drive_mode(port_handler, packet_handler, RIGHT_LEG_ID, CMD_NORMAL_MODE)
    set_drive_mode(port_handler, packet_handler, LEFT_LEG_ID, CMD_NORMAL_MODE)
    set_drive_mode(port_handler, packet_handler, RIGHT_WHEEL_ID, CMD_NORMAL_MODE)
    set_drive_mode(port_handler, packet_handler, LEFT_WHEEL_ID, CMD_NORMAL_MODE)

    time.sleep(2)

    # ドライブモードを取得して表示
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

    # 初期位置に動かす
    init_deg = 5
    set_position(port_handler, packet_handler, RIGHT_LEG_ID, init_deg)
    set_position(port_handler, packet_handler, LEFT_LEG_ID, init_deg)
    set_position(port_handler, packet_handler, RIGHT_WHEEL_ID, init_deg)
    set_position(port_handler, packet_handler, LEFT_WHEEL_ID, init_deg)

    time.sleep(2)

    # 360度回転させる
    for deg in range(5, 356):
        set_position(port_handler, packet_handler, RIGHT_LEG_ID, deg)
        set_position(port_handler, packet_handler, LEFT_LEG_ID, deg)
        set_position(port_handler, packet_handler, RIGHT_WHEEL_ID, deg)
        set_position(port_handler, packet_handler, LEFT_WHEEL_ID, deg)

    # 最終位置に動かす
    last_deg = 180
    set_position(port_handler, packet_handler, RIGHT_LEG_ID, last_deg)
    set_position(port_handler, packet_handler, LEFT_LEG_ID, last_deg)
    set_position(port_handler, packet_handler, RIGHT_WHEEL_ID, last_deg)
    set_position(port_handler, packet_handler, LEFT_WHEEL_ID, last_deg)
    time.sleep(2)

    # トルクを抜く
    set_torque(port_handler, packet_handler, RIGHT_LEG_ID, False)
    set_torque(port_handler, packet_handler, LEFT_LEG_ID, False)
    set_torque(port_handler, packet_handler, RIGHT_WHEEL_ID, False)
    set_torque(port_handler, packet_handler, LEFT_WHEEL_ID, False)


if __name__ == "__main__":
    main()
