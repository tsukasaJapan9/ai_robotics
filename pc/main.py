import time

from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Control table address
ADDR_PRO_TORQUE_ENABLE = 64  # Control table address is different in Dynamixel model
ADDR_PRO_GOAL_POSITION = 116
ADDR_PRO_PRESENT_POSITION = 132

# Protocol version
PROTOCOL_VERSION = 2.0  # See which protocol
# Default setting
DXL_ID = 1  # Dynamixel ID : 1
BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
DEVICENAME = "/dev/ttyUSB0"  # Check which port is being used on your controller
# ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
  print("Succeeded to open the port")
else:
  print("Failed to open the port")
  quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
  print("Succeeded to change the baudrate")
else:
  print("Failed to change the baudrate")
  quit()

servo_ids = range(2, 3)

for id in servo_ids:
  dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, id, ADDR_PRO_TORQUE_ENABLE, 1
  )

try:
  while True:
    for id in servo_ids:
      # Write goal position
      pos = 180
      val = int(pos / 360 * 4096)
      dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, id, ADDR_PRO_GOAL_POSITION, val
      )
    time.sleep(1)

    for id in servo_ids:
      pos = 270
      val = int(pos / 360 * 4096)
      dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(
        portHandler, id, ADDR_PRO_GOAL_POSITION, val
      )
    time.sleep(1)
except:
  print("term")

for id in servo_ids:
  dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, id, ADDR_PRO_TORQUE_ENABLE, 0
  )

# Close port
portHandler.closePort()
