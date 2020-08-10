#include "SerialCom.h"
SerialCom myTransfer;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  myTransfer.begin(Serial);

}
char ch;
byte uch;
int i;
unsigned int ui;
long l;
unsigned long ul;
float f;
bool b;
void loop() {
  if (myTransfer.available()) {
    myTransfer.readData(ch);
    myTransfer.readData(uch);
    myTransfer.readData(i);
    myTransfer.readData(ui);
    myTransfer.readData(l);
    myTransfer.readData(ul);
    myTransfer.readData(f);
    myTransfer.readData(b);
    /*Send back*/

    myTransfer.addData(ch);
    myTransfer.addData(uch);
    myTransfer.addData(i);
    myTransfer.addData(ui);
    myTransfer.addData(l);
    myTransfer.addData(ul);
    myTransfer.addData(f);
    myTransfer.addData(b);
    myTransfer.sendData();
  }
}
