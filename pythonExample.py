from SerialCom.SerialCom import *

if __name__ == '__main__':

    print(serial_ports())
    link = SerialCom('COM5')
    link.open()
    time.sleep(2)
    link.addData('H','char')
    link.addData(123, 'byte')
    link.addData(-32768, 'int')
    link.addData(65535, 'uint')
    link.addData(-2147483648, 'long')
    link.addData(4294967295, 'ulong')
    link.addData(123.456, 'float')
    link.addData(True, 'bool')
    link.send()
    print('send data...')
    while not link.available():
        if link.status < 0:
            print('ERROR: {}'.format(link.status))

    print('Response received:')
    print('status',link.status)



    print(link.readData('char'))
    print(link.readData('byte'))
    print(link.readData('int'))
    print(link.readData('uint'))
    print(link.readData('long'))
    print(link.readData('ulong'))
    print(link.readData('float'))
    print(link.readData('bool'))

    link.close()



