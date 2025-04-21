# m288/m077の仕様。ここにアドレスなどが書いてある
# https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/
# https://emanual.robotis.com/docs/en/dxl/x/xl330-m077/


from typing import Any

import dynamixel_sdk as dynamixel

ADDR_DRIVE_MODE = 10
ADDR_OPERATING_MODE = 11
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_VELOCITY = 104
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_VELOCITY = 128
ADDR_PRESENT_POSITION = 132

CMD_NORMAL_MODE = 0x00
CMD_REVERSE_MODE = 0x01
CMD_VELOCITY_CONTROL_MODE = 0x01
CMD_POSITION_CONTROL_MODE = 0x03

POSITION_LIMIT = 4095
VELOCITY_LIMIT = 2047

POSITION_UNIT = 0.088
VELOCITY_UNIT = 0.229

POSITION_RANGE_DEGREE_MIN = 0
POSITION_RANGE_DEGREE_MAX = POSITION_LIMIT * POSITION_UNIT

VELOCITY_RANGE_RPM_MIN = -VELOCITY_LIMIT * VELOCITY_UNIT
VELOCITY_RANGE_RPM_MAX = VELOCITY_LIMIT * VELOCITY_UNIT

PROTOCOL_VERSION = 2.0
BAUDRATE = 1000000
DEVICE_NAME = "/dev/ttyUSB0"

RIGHT_LEG_ID = 2
LEFT_LEG_ID = 1
RIGHT_WHEEL_ID = 3
LEFT_WHEEL_ID = 4


def create_hander() -> tuple[Any, Any]:
    port_handler = dynamixel.PortHandler(DEVICE_NAME)
    packet_handler = dynamixel.PacketHandler(PROTOCOL_VERSION)

    if port_handler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        return None, None

    if port_handler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        return None, None
    return port_handler, packet_handler


def get_last_error(
    packet_handler: Any,
    result: int,
    error: int,
) -> bool:
    if result == dynamixel.COMM_SUCCESS:
        return True

    is_error: bool = False
    _result: str = packet_handler.getTxRxResult(result)
    if _result:
        print(_result)
        is_error = True

    _error: str = packet_handler.getRxPacketError(error)
    if _error:
        print(_error)
        is_error = True
    return is_error


def set_torque(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
    enable: bool,
) -> bool:
    result, error = packet_handler.write1ByteTxRx(
        port_handler, servo_id, ADDR_TORQUE_ENABLE, 1 if enable else 0
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to set torque for servo {servo_id}, {enable}")
        return False
    return True


def set_operating_mode(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
    operating_mode: int,
) -> bool:
    result, error = packet_handler.write1ByteTxRx(
        port_handler, servo_id, ADDR_OPERATING_MODE, operating_mode
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to set operating mode for servo {servo_id}, {operating_mode}")
        return False
    return True


def get_operating_mode(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
) -> tuple[bool, int]:
    val, result, error = packet_handler.read1ByteTxRx(
        port_handler, servo_id, ADDR_OPERATING_MODE
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to get operating mode for servo {servo_id}")
        return False, -1
    return True, val


def set_drive_mode(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
    drive_mode: int,
) -> bool:
    result, error = packet_handler.write1ByteTxRx(
        port_handler, servo_id, ADDR_DRIVE_MODE, drive_mode
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to set drive mode for servo {servo_id}, {drive_mode}")
        return False
    return True


def get_drive_mode(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
) -> tuple[bool, int]:
    val, result, error = packet_handler.read1ByteTxRx(
        port_handler, servo_id, ADDR_DRIVE_MODE
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to get operating mode for servo {servo_id}")
        return False, -1
    return True, val


def set_position(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
    target_degree: float,
) -> bool:
    assert POSITION_RANGE_DEGREE_MIN <= target_degree <= POSITION_RANGE_DEGREE_MAX, (
        f"target_degree must be between {POSITION_RANGE_DEGREE_MIN} and {POSITION_RANGE_DEGREE_MAX}"
    )
    val = int(target_degree / POSITION_UNIT)
    result, error = packet_handler.write4ByteTxRx(
        port_handler, servo_id, ADDR_GOAL_POSITION, val
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to set drive mode for servo {servo_id}, {target_degree}")
        return False
    return True


def get_position(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
) -> tuple[bool, int]:
    val, result, error = packet_handler.read4ByteTxRx(
        port_handler, servo_id, ADDR_PRESENT_POSITION
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to get position for servo {servo_id}")
        return False, -1
    return True, val * POSITION_UNIT


def set_velocity(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
    target_rpm: float,
) -> bool:
    assert VELOCITY_RANGE_RPM_MIN <= target_rpm <= VELOCITY_RANGE_RPM_MAX, (
        f"target_rpm must be between {VELOCITY_RANGE_RPM_MIN} and {VELOCITY_RANGE_RPM_MAX}"
    )
    val = int(target_rpm / VELOCITY_UNIT)
    result, error = packet_handler.write4ByteTxRx(
        port_handler, servo_id, ADDR_GOAL_VELOCITY, val
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to set velocity for servo {servo_id}, {val}")
        return False
    return True


def to_signed(val: int) -> int:
    if val >= 0x80000000:
        return val - 0x100000000
    else:
        return val


def get_velocity(
    port_handler: dynamixel.PortHandler,
    packet_handler: Any,
    servo_id: int,
) -> tuple[bool, float]:
    val, result, error = packet_handler.read4ByteTxRx(
        port_handler, servo_id, ADDR_PRESENT_VELOCITY
    )

    if not get_last_error(packet_handler, result, error):
        print(f"Failed to get velocity for servo {servo_id}")
        return False, -1
    return True, to_signed(val) * VELOCITY_UNIT
