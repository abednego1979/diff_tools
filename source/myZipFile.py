# -*- coding: utf-8 -*-

#Python 3.5

import zipfile
import os


__metaclass__ = type
    
    
class myZipFile():
    def myZipFile(self, infileList, outZipfile):
        f = zipfile.ZipFile(outZipfile,'w',zipfile.ZIP_DEFLATED)
        for item in infileList:
            f.write(item)
        f.close()

    def myUnzipFile(self, inZipFile):
        temp=[]
        zfile = zipfile.ZipFile(inZipFile,'r')
        for filename in zfile.namelist():
            data = zfile.read(filename)
            pf = open(filename+'.1', 'w+b')
            pf.write(data)
            pf.close()
            temp.append(filename+'.1')
    
        return temp





