# SerialCom
This project adaptform SerialTransfer and pySerialTranfer for more simple, convenience in implementation and more compatibillity with Arduino data type.
This project only support Serial UART comunication with simple variable type including bool, char, byte, int, unsigned int, long, unsigned long and float.
### Added
 - Implement addData(), readData() for more convenience.
 - Add Specific data type for python.

### Removed
 - String, List and Dict transfer from python.
 - Struct transfer from Arduino.
 - Arduino debug port.
 
 # Python guide
 
 ## Port setup
```
   from SerialCom.SerialCom import *
   print(serial_ports()) # Show available port
   link = SerialCom('COM5') # Select port
   link.open() # Connect to port
   time.sleep(2) # Wait for Arduino boot up
```
 ## Send data
 Simply use addData() too add data to txBuffer then call send(). remember, order of addData must be match with reciever.
 ```
    link.addData('H','char')
    link.addData(123, 'byte')
    link.addData(-32768, 'int')
    link.addData(65535, 'uint')
    link.addData(-2147483648, 'long')
    link.addData(4294967295, 'ulong')
    link.addData(123.456, 'float')
    link.addData(True, 'bool')
    link.send()
 ```
  ## Receive data
  
  You can use this block to wait for data.
  ```
      while not link.available():
        if link.status < 0:
            print('ERROR: {}'.format(link.status))
       # data available to read here!.
  ```
  Or use this block for check if data ready to read.
  ```
      while True: # Main loop
        if link.available()::
            # data available to read here!.
  ```
  To read data just use readData() with specify data type.
  For proper reading you must know exact data type and order of data in packet.
  
  ```
    print(link.readData('char'))
    print(link.readData('byte'))
    print(link.readData('int'))
    print(link.readData('uint'))
    print(link.readData('long'))
    print(link.readData('ulong'))
    print(link.readData('float'))
    print(link.readData('bool'))
  ```
   # Arduino guide
   
   ## Port setup
   use 115200 as default baudrate.
   ```
#include "SerialCom.h"
SerialCom myTransfer;
void setup() {
    Serial.begin(115200);
    myTransfer.begin(Serial);
}
```
  ## Send data
  use addData to story data to txBuffer (data type will detect automatically).
  Then call sendData() to send data.
  ```
    myTransfer.addData(ch);
    myTransfer.addData(uch);
    myTransfer.addData(i);
    myTransfer.addData(ui);
    myTransfer.addData(l);
    myTransfer.addData(ul);
    myTransfer.addData(f);
    myTransfer.addData(b);
    myTransfer.sendData();
  ```
    ## Receive data
Use readData in correct order and data type. the function will pass data by reference.

```
if (myTransfer.available()) {
    myTransfer.readData(ch);
    myTransfer.readData(uch);
    myTransfer.readData(i);
    myTransfer.readData(ui);
    myTransfer.readData(l);
    myTransfer.readData(ul);
    myTransfer.readData(f);
    myTransfer.readData(b);
    }
 ```
