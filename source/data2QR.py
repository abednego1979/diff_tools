# -*- coding: utf-8 -*-

#Python 2.7.x

import base64
import datetime

__metaclass__ = type

class myCrypt():
    
    def encrypt(self, filename, pw):
        b=''
        try:
            with open (filename, 'rb') as pf:
                s=bytearray(pf.read())
                for index in range(len(s)):
                    try:
                        s[index]+=pw
                    except:
                        s[index]-=(256-pw)
                b=base64.b64encode(s)
        except:
            print 'encrypt fail'
        
        return b

    def decrypt(self, inputString, pw, filename):
        b=base64.b64decode(inputString)
        s=bytearray(b)
        for index in range(len(s)):
            try:
                s[index]-=pw
            except:
                s[index]+=(256-pw)
        try:
            with open (filename, 'wb') as pf:
                pf.write(s)
        except:
            print 'decrypt fail'
