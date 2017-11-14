import serial
import binascii
from Log import *

logger = Log(__name__).getlog()


class DLT645_2007Protocol():

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
        command[9] = address[2:4]
        command[10] = address[0:2]
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
            logger.info("CScheck success")
            dataLen = int(''.join(resData[9:10]),16)
            if(''.join(resData[10+dataLen:11+dataLen]).upper() == _len):
                logger.info("dataLen success")
                return dataLen
            else:
                logger.error("dataLen fails")
                return 0
        else:
            logger.error("CScheck fails")
            return 0

    def analysisData(self,data):
        resData = self.toListData(data)
        dataLen = self.checkData(data)
        if dataLen < 1:
            logger.error("read data fail")
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
        return int(''.join(dataList[0:-4]))

    def sendData(self,data,_address,ser):
        cmd = self.structCmd(_address,data)
        command = binascii.unhexlify(''.join(cmd))
        ser.write(command)
        response = ser.readall()
        ser.flushInput()
        return response

    def sendCmd(self,send):
        A_voltage_send = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '34', '34', '35', '4B', '16']
        B_voltage_send = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '35', '34', '35', '4B', '16']
        C_voltage_send = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '36', '34', '35', '4B', '16']
        A_current_send = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '34', '35', '35', '4B', '16']
        B_current_send = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '35', '35', '35', '4B', '16']
        C_current_send = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '36', '35', '35', '4B', '16']
        all_energy = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '33', '34', '33', '4B', '16']
        all_power = ['FE','FE','FE','FE', '68', '40', '56', '03', '00', '00', '00', '68', '11', '04', '33', '33', '36', '35', '4B', '16']

        dataList = []

        sendlist = send.split(",")
        logger.info(str(sendlist[0]))
        Adress =str(sendlist[0])
        _address = Adress.zfill(12)
        _parity = str(sendlist[3])
        _bytesize= int(sendlist[4])
        _stopbits = int(sendlist[5])
        _timeout = int(sendlist[6])

        ser = serial.Serial(port=str(sendlist[1]), baudrate=str(sendlist[2]), parity=_parity,bytesize=_bytesize, stopbits=_stopbits, timeout=_timeout)
        print "serial.isOpen()=",ser.isOpen()
        if ser.is_open :
            response = self.sendData(all_energy,_address,ser)
            all_energy_data = self.analysisData(binascii.hexlify(response))/100.00
            if all_energy_data < 0 :
                return -1
            print "all_energyData:",all_energy_data
            dataList.append(str(all_energy_data))

            response = self.sendData(all_power,_address,ser)
            all_power_data = self.analysisData(binascii.hexlify(response))/10000.0000
            if all_power_data < 0 :
                return -1
            print "all_powerData:",all_power_data
            dataList.append(str(all_power_data))

            response = self.sendData(A_voltage_send,_address,ser)
            A_voltage = self.analysisData(binascii.hexlify(response))/10.0
            if A_voltage < 0:
                return -1
            print "A_voltage:",A_voltage
            dataList.append(str(A_voltage))

            response = self.sendData(B_voltage_send,_address,ser)
            B_voltage = self.analysisData(binascii.hexlify(response))/10.0
            if B_voltage < 0:
                return -1
            print "B_voltage:",B_voltage
            dataList.append(str(B_voltage))

            response = self.sendData(C_voltage_send,_address,ser)
            C_voltage = self.analysisData(binascii.hexlify(response))/10.0
            if C_voltage < 0:
                return -1
            print"C_voltage:",C_voltage
            dataList.append(str(C_voltage))

            response = self.sendData(A_current_send,_address,ser)
            A_current = self.analysisData(binascii.hexlify(response))/1000.000
            if A_current < 0:
                return -1
            print "A_voltage:", A_current
            dataList.append(str(A_current))

            response = self.sendData(B_current_send,_address,ser)
            B_current = self.analysisData(binascii.hexlify(response))/1000.000
            if B_current < 0:
                return -1
            print "B_voltage:", B_current
            dataList.append(str(B_current))

            response = self.sendData(C_current_send,_address,ser)
            C_current = self.analysisData(binascii.hexlify(response))/1000.000
            if C_current < 0:
                return -1
            print "C_voltage:",C_current
            dataList.append(str(C_current))

            ser.close()
            print "serial.isOpen()=",ser.isOpen()
            return dataList
        else:
            return -1
