#include "SerialCom.h"
SerialCom myTransfer;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  myTransfer.begin(Serial);

}

void loop() {
  float x = float(millis() % 1000) * TWO_PI / 1000.0;
  float y = sin(x);
  myTransfer.addData(millis());
  myTransfer.addData(y);

  myTransfer.sendData();

  delay(5);
}
