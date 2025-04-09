# m288/m077の仕様。ここにアドレスなどが書いてある
# https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/
# https://emanual.robotis.com/docs/en/dxl/x/xl330-m077/

import sys
import time

import dynamixel_sdk as dynamixel

ADDR_DRIVE_MODE = 10
ADDR_OPERATING_MODE = 10
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


def get_last_error(
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
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
  packet_handler: dynamixel.PacketHandler,
  servo_id: int,
) -> tuple[bool, int]:
  val, result, error = packet_handler.read4ByteTxRx(
    port_handler, servo_id, ADDR_PRESENT_VELOCITY
  )

  if not get_last_error(packet_handler, result, error):
    print(f"Failed to get velocity for servo {servo_id}")
    return False, -1
  return True, to_signed(val) * VELOCITY_UNIT


def main() -> None:
  port_handler = dynamixel.PortHandler(DEVICE_NAME)
  packet_handler = dynamixel.PacketHandler(PROTOCOL_VERSION)

  if port_handler.openPort():
    print("Succeeded to open the port")
  else:
    print("Failed to open the port")
    sys.exit(1)

  if port_handler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
  else:
    print("Failed to change the baudrate")
    sys.exit(1)

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

  # set_position(port_handler, packet_handler, RIGHT_LEG_ID, 0)
  # set_position(port_handler, packet_handler, LEFT_LEG_ID, 0)
  # time.sleep(1)
  # for i in range(361):
  #   set_position(port_handler, packet_handler, RIGHT_LEG_ID, i)
  #   set_position(port_handler, packet_handler, LEFT_LEG_ID, i)
  #   _, pos = get_position(port_handler, packet_handler, RIGHT_LEG_ID)
  #   print(f"ID: {RIGHT_LEG_ID}, position: {pos}")
  #   _, pos = get_position(port_handler, packet_handler, LEFT_LEG_ID)
  #   print(f"ID: {LEFT_LEG_ID}, position: {pos}")

  # time.sleep(1)
  # _, pos = get_position(port_handler, packet_handler, RIGHT_LEG_ID)
  # print(f"ID: {RIGHT_LEG_ID}, position: {pos}")
  # _, pos = get_position(port_handler, packet_handler, LEFT_LEG_ID)
  # print(f"ID: {LEFT_LEG_ID}, position: {pos}")

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
