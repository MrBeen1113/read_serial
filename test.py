__author__ = 'zhaopeng'

from DLT645_2007Protocol import *


if __name__ == '__main__':

    p2007 = DLT645_2007Protocol()
    #267080,/dev/ttyO1,2400,E,8,1,1
    send = raw_input("enter your input :")
    print "received input is:" , send

    b = p2007.sendCmd(send)
    print b
