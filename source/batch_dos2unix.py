# -*- coding: UTF-8 -*-
#python 3.5


import os
import platform

__metaclass__ = type


class batch_dos2unix():
    typeList=[]
    
    def __isWindowsSystem__(self):
        return 'Windows' in platform.system()
    def __isLinuxSystem__(self):
        return 'Linux' in platform.system()

    def checkEnv(self):
        if self.__isWindowsSystem__():
            if os.path.isfile('dos2unix.exe'):
                return True
            else:
                print ('"dos2unix.exe" is not exist')
                return False
        elif self.__isLinuxSystem__():
            return True
        else:
            assert 0,'Unknown System Type'
        
    def setProcFileType(self, typeList=[]):
        self.typeList=typeList
    
    
    def __dos2unix__(self, inFile):
        
        f=os.path.splitext(inFile)
        
        if not self.typeList:
            pass#未限制,所有类型的文件都需要做一下dos2unix的变换
        else:
            if f[1] not in self.typeList:
                return
            else:
                pass
        
        #现在开始处理
        if self.__isWindowsSystem__():
            os.system('dos2unix %s' % inFile)
        elif self.__isLinuxSystem__():
            os.system('fromdos %s' % inFile)
        else:
            assert 0,'Unknown System Type'
        
        return

    def dos2unix_file(self, inFile):
        self.__dos2unix__(inFile)
        
    def dos2unix_dir(self, inDir):
        if os.path.isdir(inDir):
            for parent,dirnames,filenames in os.walk(inDir):
                for filename in filenames:
                    self.__dos2unix__(os.path.join(parent,filename))
        
        

