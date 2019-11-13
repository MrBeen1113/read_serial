__author__ = 'zhaopeng'

import serial
import binascii
import time
import logging


class DLT645_1997Protocol():

    def __init__(self):
        pass

    def calcSum(self,l):
        verify_sum = 0
        for val_str in l:
            verify_sum += int(val_str, 16)
        return hex(verify_sum % 256).upper()[2:].zfill(2)

    def structCmd(self,address,data):
        command = data[:]
        command[5] = address[10:12]
        command[6] = address[8:10]
        command[7] = address[6:8]
        command[8] = address[4:6]
        checkSum = self.calcSum(command[4:-2])
        command[-2] = checkSum
        print "send_data",command
        return command

    def toListData(self,data):
        resData = []
        count = len(data)
        i = 0
        j = 0
        while (i < count):
            resData.append(data[i:i+2])
            j = j + 1; i = i + 2
        print "toListData:",resData
        return resData

    def checkData(self,data):
        resData = self.toListData(data)
        checkLen = str(self.calcSum(resData[0:-2]))
        _len = ''.join(resData[-2:-1]).upper()
        if checkLen == _len:
            logging.info("CScheck success")
            dataLen = int(''.join(resData[9:10]),16)
            if(''.join(resData[10+dataLen:11+dataLen]).upper() == _len):
                logging.info("dataLen success")
                return dataLen
            else:
                logging.error("dataLen fails")
                return -1
        else:
            logging.error("CScheck fails")
            return -1

    def analysisData(self,data):
        resData = self.toListData(data[2:])
        dataLen = self.checkData(data[2:])
        if dataLen < 1:
            logging.error("read data fail")
            return -1

        i=1
        while(i <= dataLen):
            dataA = int(''.join(resData[9+i]),16) - int('33',16)
            dataB = hex(dataA).upper()[2:].zfill(2)
            resData[9+i] = dataB
            i = i+1

        dataList_b = resData[10:10+dataLen]
        dataList = resData[10:10+dataLen]
        for i in dataList_b:
            dataList[dataLen -1] = i
            dataLen = dataLen - 1
        print dataList
        print int(''.join(dataList))
        return int(''.join(dataList))

    def sendData(self,data,_address,ser):
        cmd = self.structCmd(_address,data)
        command = binascii.unhexlify(''.join(cmd))
        ser.write(command)
        response = ser.readall()
        ser.flushInput()
        return response

    def sendCmd(self, Adress, _port, _baudrate, _parity, _bytesize, _stopbits, _timeout):

        all_energy = ['FE','FE','FE','FE','68', '19', '77', '91', '00', '01', '02', '68', '01', '02', '43', 'C3', 'FD', '16']

        dataList = []

        _address = Adress.zfill(12)
        print _address
        try:
            ser = serial.Serial(port=_port, baudrate=_baudrate, parity=_parity, bytesize=_bytesize, stopbits=_stopbits, timeout=_timeout)
            logging.info("elec open serial ok!")
        except:
            logging.error("elec open serial fail")
            return -1

        print "serial.isOpen()=",ser.isOpen()
        if ser.is_open :
            response = self.sendData(all_energy,_address,ser)
            # print response
            all_energy_data = self.analysisData(binascii.hexlify(response))/1000000.000000
            if all_energy_data < 0 :
                ser.close()
                return -1
            print "all_energyData:",all_energy_data
            dataList.append(str(all_energy_data))

            ser.close()
            print "serial.isOpen()=",ser.isOpen()

            timestamp = time.time()
            timestruct = time.localtime(timestamp)
            currTime = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
            dataList.append(currTime)

            return dataList
        else:
            logging.error("serial.isClose")
            return -1
