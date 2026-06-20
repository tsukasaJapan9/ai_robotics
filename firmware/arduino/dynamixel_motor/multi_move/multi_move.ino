/*******************************************************************************
* Copyright 2016 ROBOTIS CO., LTD.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

#include <DynamixelShield.h>

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)
  #include <SoftwareSerial.h>
  SoftwareSerial soft_serial(7, 8); // DYNAMIXELShield UART RX/TX
  #define DEBUG_SERIAL soft_serial
#elif defined(ARDUINO_SAM_DUE) || defined(ARDUINO_SAM_ZERO)
  #define DEBUG_SERIAL SerialUSB    
#else
  #define DEBUG_SERIAL Serial
#endif

const uint8_t DXL_ID1 = 1;
const uint8_t DXL_ID2 = 2;
const uint8_t DXL_ID3 = 3;
const uint8_t DXL_ID4 = 4;
const float DXL_PROTOCOL_VERSION = 2.0;

DynamixelShield dxl;

//This namespace is required to use Control table item names
using namespace ControlTableItem;

void setup() {
  // put your setup code here, to run once:
  
  // For Uno, Nano, Mini, and Mega, use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);

  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  dxl.begin(57600);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  // Get DYNAMIXEL information
  dxl.ping(DXL_ID1);
  dxl.ping(DXL_ID2);
  dxl.ping(DXL_ID3);
  dxl.ping(DXL_ID4);

  // Turn off torque when configuring items in EEPROM area
  dxl.torqueOff(DXL_ID1);
  dxl.torqueOff(DXL_ID2);
  dxl.torqueOff(DXL_ID3);
  dxl.torqueOff(DXL_ID4);
  dxl.setOperatingMode(DXL_ID1, OP_POSITION);
  dxl.setOperatingMode(DXL_ID2, OP_POSITION);
  dxl.setOperatingMode(DXL_ID3, OP_POSITION);
  dxl.setOperatingMode(DXL_ID4, OP_POSITION);
  dxl.torqueOn(DXL_ID1);
  dxl.torqueOn(DXL_ID2);
  dxl.torqueOn(DXL_ID3);
  dxl.torqueOn(DXL_ID4);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  // Please refer to e-Manual(http://emanual.robotis.com/docs/en/parts/interface/dynamixel_shield/) for available range of value. 
  // Set Goal Position in RAW value
  dxl.setGoalPosition(DXL_ID1, 210, UNIT_DEGREE);
  dxl.setGoalPosition(DXL_ID2, 210, UNIT_DEGREE);
  dxl.setGoalPosition(DXL_ID3, 210, UNIT_DEGREE);
  dxl.setGoalPosition(DXL_ID4, 210, UNIT_DEGREE);
  delay(1000);
  // Print present position in raw value
  DEBUG_SERIAL.println("Present Position(degree) : ");
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID1, UNIT_DEGREE));
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID2, UNIT_DEGREE));
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID3, UNIT_DEGREE));
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID4, UNIT_DEGREE));
  delay(1000);

  // Set Goal Position in DEGREE value
  dxl.setGoalPosition(DXL_ID1, 330, UNIT_DEGREE);
  dxl.setGoalPosition(DXL_ID2, 330, UNIT_DEGREE);
  dxl.setGoalPosition(DXL_ID3, 330, UNIT_DEGREE);
  dxl.setGoalPosition(DXL_ID4, 330, UNIT_DEGREE);
  delay(1000);
  // Print present position in degree value
  DEBUG_SERIAL.println("Present Position(degree) : ");
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID1, UNIT_DEGREE));
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID2, UNIT_DEGREE));
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID3, UNIT_DEGREE));
  DEBUG_SERIAL.println(dxl.getPresentPosition(DXL_ID4, UNIT_DEGREE));
  delay(1000);
}
