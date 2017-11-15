# -*- coding: utf-8 -*-

#Python 3.5

import base64
import datetime
import json
from aes import AESCrypto

__metaclass__ = type

class myCrypt():
    
    def encryptFile(self, filename, key):
        try:
            with open (filename, 'rb') as pf:
                message=pf.read()
                message = AESCrypto(key, b'0000000000000000').encrypt(message)
                message=base64.b64encode(message)
        except:
            print ('encrypt fail')
        
        return message

    def decryptFile(self, message, key, filename):
        message = base64.b64decode(message)
        message=AESCrypto(key, b'0000000000000000').decrypt(message)
        try:
            with open (filename, 'wb') as pf:
                pf.write(message)
        except:
            print ('decrypt fail')
