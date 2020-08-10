#include "SerialCom.h"


/*
 void SerialCom::begin(Stream &_port)
 Description:
 ------------
  * Initializer for the SerialCom Class
 Inputs:
 -------
  * const Stream &_port - Serial port to communicate over
  
 Return:
 -------
  * void
*/
void SerialCom::begin(Stream& _port)
{
	port = &_port;
	
}





/*
 uint8_t SerialCom::sendData(const uint16_t &messageLen, const uint8_t packetID)
 Description:
 ------------
  * Send a specified number of bytes in packetized form
 Inputs:
 -------
  * const uint16_t &messageLen - Number of values in txBuff
  to send as the payload in the next packet
  * const uint8_t packetID - The packet 8-bit identifier
 Return:
 -------
  * uint8_t numBytesIncl - Number of payload bytes included in packet
*/
uint8_t SerialCom::sendData(const uint16_t& messageLen, const uint8_t packetID)
{

	uint8_t numBytesIncl;

	numBytesIncl = packet.constructPacket(messageLen, packetID);
	
	port->write(packet.preamble, sizeof(packet.preamble));
	port->write(packet.txBuff, numBytesIncl);
	port->write(packet.postamble, sizeof(packet.postamble));
	crr_addData_idx = 0;
	return numBytesIncl;
}
uint8_t SerialCom::sendData(const uint8_t packetID)
{		

	uint8_t numBytesIncl;

	numBytesIncl = packet.constructPacket(crr_addData_idx, packetID);
	
	port->write(packet.preamble, sizeof(packet.preamble));
	port->write(packet.txBuff, numBytesIncl);
	port->write(packet.postamble, sizeof(packet.postamble));

	/*
	port->println("sendData");

	for (int i=0;i<crr_addData_idx;i++){
	port->println(packet.txBuff[i]);
	}
	*/
	crr_addData_idx = 0;
	return numBytesIncl;
}


/*
 uint8_t SerialCom::available()
 Description:
 ------------
  * Parses incoming serial data, analyzes packet contents,
  and reports errors/successful packet reception
 Inputs:
 -------
  * void
 Return:
 -------
  * uint8_t bytesRead - Num bytes in RX buffer
*/
uint8_t SerialCom::available()
{
	bool    valid   = false;
	uint8_t recChar = 0xFF;

	if (port->available())
	{
		valid = true;

		while (port->available())
		{
			recChar = port->read();

			bytesRead = packet.parse(recChar, valid);
			status    = packet.status;
		}
	}
	else
	{
		bytesRead = packet.parse(recChar, valid);
		status    = packet.status;
	}
	
	if (packet.status == NEW_DATA){
	crr_readData_idx = 0;
	}
	return bytesRead;
}




/*
 uint8_t SerialCom::currentPacketID()
 Description:
 ------------
  * Returns the ID of the last parsed packet
 Inputs:
 -------
  * void
 Return:
 -------
  * uint8_t - ID of the last parsed packet
*/
uint8_t SerialCom::currentPacketID()
{
	return packet.currentPacketID();
}
