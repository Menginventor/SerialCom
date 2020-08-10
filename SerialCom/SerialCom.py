import serial
import serial.tools.list_ports
import struct
import time
from .CRC import CRC
START_BYTE = 0x7E
STOP_BYTE  = 0x81
find_start_byte    = 0
find_id_byte       = 1
find_overhead_byte = 2
find_payload_len   = 3
find_payload       = 4
find_crc           = 5
find_end_byte      = 6
CONTINUE        = 3
NEW_DATA        = 2
NO_DATA         = 1
CRC_ERROR       = 0
PAYLOAD_ERROR   = -1
STOP_BYTE_ERROR = -2

def serial_ports():
    return [p.device for p in serial.tools.list_ports.comports(include_links=True)]


class SerialCom(object):
    def __init__(self, port_name, baud=115200,MAX_PACKET_SIZE = 32):
        self.MAX_PACKET_SIZE = MAX_PACKET_SIZE
        self.addData_idx = 0
        self.readData_idx = 0
        self.txBuff = [' ' for i in range(MAX_PACKET_SIZE - 1)]
        self.rxBuff = [' ' for i in range(MAX_PACKET_SIZE - 1)]
        self.port_name = port_name
        self.overheadByte = 0xFF
        #
        self.crc = CRC()
        self.connection = serial.Serial()
        self.connection.port = self.port_name
        self.connection.baudrate = baud
        self.state = find_start_byte
    def addData(self,val,data_type):
        format_str = ''
        if data_type == 'byte':
            if type(val) == str :
                if len(val) != 1:
                    return None
                format_str = '1s'
                val = val.encode()

            if type(val) == int:
                format_str = 'B'

        elif data_type == 'char':
            if type(val) == str :
                if len(val) == 1:
                    format_str = '1s'
                    val = val.encode()
            if type(val) == int:
                format_str = 'b'
        else:
            conversion_dict = {
                'bool': '?',
                'int':'h',
                'uint': 'H',
                'long': 'l',
                'ulong': 'L',
                'float': 'f',
            }
            if data_type in conversion_dict:
                format_str = conversion_dict[data_type]
            else:
                return None



        val_bytes = struct.pack(format_str, val)
        for idx in range(len(val_bytes)):
            self.txBuff[idx + self.addData_idx] = val_bytes[idx]
        self.addData_idx += len(val_bytes)

    def send(self, packet_id=0):
        '''
        Description:
        ------------
        Send a specified number of bytes in packetized form

        :param message_len: int - number of bytes from the txBuff to send as
                                  payload in the packet

        :return: bool - whether or not the operation was successful
        '''

        stack = []
        message_len = self.addData_idx

        try:


            self.calc_overhead(message_len)
            self.stuff_packet(message_len)
            found_checksum = self.crc.calculate(self.txBuff, message_len)


            stack.append(START_BYTE)
            stack.append(packet_id)
            stack.append(self.overheadByte)
            stack.append(message_len)

            for i in range(message_len):
                if type(self.txBuff[i]) == str:
                    val = ord(self.txBuff[i])
                else:
                    val = int(self.txBuff[i])

                stack.append(val)

            stack.append(found_checksum)
            stack.append(STOP_BYTE)

            stack = bytearray(stack)

            if self.open():

                self.connection.write(stack)

            return True

        except:
            import traceback
            traceback.print_exc()

            return False

    def calc_overhead(self, pay_len):
        '''
        Description:
        ------------
        Calculates the COBS (Consistent Overhead Stuffing) Overhead
        byte and stores it in the class's overheadByte variable. This
        variable holds the byte position (within the payload) of the
        first payload byte equal to that of START_BYTE
        :param pay_len: int - number of bytes in the payload
        :return: void
        '''

        self.overheadByte = 0xFF

        for i in range(pay_len):
            if self.txBuff[i] == START_BYTE:
                self.overheadByte = i
                break

    def find_last(self, pay_len):
        '''
        Description:
        ------------
        Finds last instance of the value START_BYTE within the given
        packet array

        :param pay_len: int - number of bytes in the payload

        :return: int - location of the last instance of the value START_BYTE
                       within the given packet array
        '''
        
        if pay_len <= self.MAX_PACKET_SIZE:

            for i in range(pay_len - 1, -1, -1):

                if self.txBuff[i] == START_BYTE:

                    return i
        return -1

    def stuff_packet(self, pay_len):
        '''
        Description:
        ------------
        Enforces the COBS (Consistent Overhead Stuffing) ruleset across
        all bytes in the packet against the value of START_BYTE

        :param pay_len: int - number of bytes in the payload

        :return: void
        '''

        refByte = self.find_last(pay_len)

        if (not refByte == -1) and (refByte <= self.MAX_PACKET_SIZE):
            for i in range(pay_len - 1, -1, -1):
                if self.txBuff[i] == START_BYTE:
                    self.txBuff[i] = refByte - i
                    refByte = i
    def open(self):
        '''
        Description:
        ------------
        Open serial port and connect to device if possible

        :return: bool - True if successful, else False
        '''

        if not self.connection.is_open:
            try:
                self.connection.open()
                return True
            except serial.SerialException as e:
                print(e)
                return False
        return True
    def close(self):
        '''
        Description:
        ------------
        Close serial port

        :return: void
        '''
        if self.connection.is_open:
            self.connection.close()
    def clear_packet(self):
        self.addData_idx = 0
    
    def unpack_packet(self, pay_len):
        '''
        Description:
        ------------
        Unpacks all COBS-stuffed bytes within the array

        :param pay_len: int - number of bytes in the payload

        :return: void
        '''

        testIndex = self.recOverheadByte
        delta = 0

        if testIndex <= self.MAX_PACKET_SIZE:
            while self.rxBuff[testIndex]:
                delta = self.rxBuff[testIndex]
                self.rxBuff[testIndex] = START_BYTE
                testIndex += delta

            self.rxBuff[testIndex] = START_BYTE
    
    def available(self):
        '''
        Description:
        ------------
        Parses incoming serial data, analyzes packet contents,
        and reports errors/successful packet reception

        :return self.bytesRead: int - number of bytes read from the received
                                      packet
        '''
        if self.open():
            if self.connection.in_waiting:
                while self.connection.in_waiting:
                    recChar = int.from_bytes(self.connection.read(),byteorder='big')

                    if self.state == find_start_byte:
                        if recChar == START_BYTE:
                            self.state = find_id_byte

                    elif self.state == find_id_byte:
                        self.idByte = recChar
                        self.state = find_overhead_byte

                    elif self.state == find_overhead_byte:
                        self.recOverheadByte = recChar
                        self.state = find_payload_len

                    elif self.state == find_payload_len:
                        if recChar <= self.MAX_PACKET_SIZE:
                            self.bytesToRec = recChar
                            self.payIndex = 0
                            self.state = find_payload
                        else:
                            self.bytesRead = 0
                            self.state = find_start_byte
                            self.status = PAYLOAD_ERROR
                            return self.bytesRead

                    elif self.state == find_payload:
                        if self.payIndex < self.bytesToRec:
                            self.rxBuff[self.payIndex] = recChar
                            self.payIndex += 1

                            if self.payIndex == self.bytesToRec:
                                self.state = find_crc

                    elif self.state == find_crc:
                        found_checksum = self.crc.calculate(
                            self.rxBuff, self.bytesToRec)

                        if found_checksum == recChar:
                            self.state = find_end_byte
                        else:
                            self.bytesRead = 0
                            self.state = find_start_byte
                            self.status = CRC_ERROR
                            return self.bytesRead

                    elif self.state == find_end_byte:
                        self.state = find_start_byte

                        if recChar == STOP_BYTE:
                            self.unpack_packet(self.bytesToRec)
                            self.bytesRead = self.bytesToRec
                            self.status = NEW_DATA
                            self.readData_idx = 0

                            return self.bytesRead

                        self.bytesRead = 0
                        self.status = STOP_BYTE_ERROR
                        return self.bytesRead

                    else:
                        print('ERROR: Undefined state: {}'.format(self.state))
                        self.bytesRead = 0
                        self.state = find_start_byte
                        return self.bytesRead
            else:
                self.bytesRead = 0
                self.status = NO_DATA
                return self.bytesRead

        self.bytesRead = 0
        self.status = CONTINUE
        return self.bytesRead

    def readData(self, obj_type):
        '''
        Description:
        ------------
        Extract an arbitrary variable's value from the RX buffer starting at
        the specified index. If object_type is list, it is assumed that the
        list to be extracted has homogeneous element types where the common
        element type can neither be list, dict, nor string longer than a
        single char

        :param obj_type:      type - type of object to extract from the RX buffer
        :param obj_byte_size: int  - number of bytes making up extracted object
        :param start_pos:     int  - index of TX buffer where the first byte
                                     of the value is to be stored in
        :param list_format:   char - array.array format char to represent the
                                     common list element type - 'c' for a char
                                     list is supported

        :return unpacked_response: obj - object extracted from the RX buffer,
                                         None if operation failed
        '''
        data_size = {
            'bool': 1,
            'byte': 1,
            'char': 1,
            'int': 2,
            'uint': 2,
            'long': 4,
            'ulong': 4,
            'float': 4,
        }

        conversion_dict = {
            'bool': '?',
            'byte': 'B',
            'char': 'c',
            'int': 'h',
            'uint': 'H',
            'long': 'l',
            'ulong': 'L',
            'float': 'f',
        }
        if obj_type not in data_size:
            return None




        buff = bytes(self.rxBuff[self.readData_idx:(self.readData_idx + data_size[obj_type])])
        self.readData_idx += data_size[obj_type]
        #
        format_str = conversion_dict[obj_type]

        unpacked_response = struct.unpack(format_str, buff)[0]

        if obj_type == 'char':
            unpacked_response = unpacked_response.decode('utf-8')



        return unpacked_response

if __name__ == '__main__':
    crc = CRC()
    print(serial_ports())
    link = SerialCom('COM5')
    link.open()
    time.sleep(2)
    link.addData(START_BYTE,'byte')

    link.addData(1.123, 'float')
    link.addData('H', 'char')
    link.send()
    while not link.available():
        if link.status < 0:
            print('ERROR: {}'.format(link.status))

    print('Response received:')
    print('status',link.status)
    response = ''
    for index in range(link.bytesRead):
        print(link.rxBuff[index])

    print(link.readData('byte'))
    print(link.readData('float'))
    print(link.readData('char'))
    link.close()


