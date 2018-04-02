# -*- coding: utf-8 -*-

#Python 3.5

import base64
import datetime
import json
import math
import random
from aes import AESCrypto

__metaclass__ = type

class myCrypt():
    
    #将二进制数据转化为汉字
    def transData2Chinese(self, message, table):
        message+=b'####'
        outMessage=[]
        gBitPos=0
    
        rawMesLen=len(message)
        #由于每11个bit转化为一个汉字，那么先将message补充足够的0
        message+=b'\x00\x00'
        while gBitPos<rawMesLen*8:
            #从bitPos读取5bit，再读取6bit
            #先计算byte位置
            bytePos=int(gBitPos/8)
            bitPos=int(gBitPos%8)
            byte0=message[bytePos]
            byte1=message[bytePos+1]
            byte2=message[bytePos+2]
            allBytes=byte0+256*byte1+256*256*byte2
            allBytes >>= bitPos
            bit5=allBytes&31
            allBytes >>= 5
            bit6=allBytes&63
    
            outMessage.append(table[bit5+bit6*32])
    
            gBitPos+=11
        return ''.join(outMessage)
    
    def transChinese2Data(self, message, table):
        outMessage=b''
        bitBuffer=0
        bitBufLen=0
        for char in message:
            bitBuffer |= table.index(char)<<bitBufLen
            bitBufLen+=11                        
            while bitBufLen>=8:
                temp=bitBuffer&255
                bitBuffer>>=8
                bitBufLen-=8
                outMessage+=temp.to_bytes(1, byteorder='big')
        
        while outMessage[-1]!=b'#'[0]:
            outMessage=outMessage[:-1]
        assert outMessage[-4:]==b'####'
        outMessage=outMessage[:-4]
        return outMessage
    
    def encryptFile(self, filename, key, table=[]):
        try:
            with open (filename, 'rb') as pf:
                message=pf.read()
                message = AESCrypto(key, b'0000000000000000').encrypt(message)
                if not table:
                    message=base64.b64encode(message)
                else:
                    #将二进制数据转化为汉字
                    message = self.transData2Chinese(message, table)                    
        except:
            print ('encrypt fail')
        
        return message

    def decryptFile(self, message, key, filename, table=[]):
        if not table:
            message = base64.b64decode(message)
        else:
            #解码汉字为二进制数据
            message = self.transChinese2Data(message, table)        
        message=AESCrypto(key, b'0000000000000000').decrypt(message)
        try:
            with open (filename, 'wb') as pf:
                pf.write(message)
        except:
            print ('decrypt fail')
