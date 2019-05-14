# -*- coding: utf-8 -*-

#Python 3.5

import os
import base64
import datetime
import json
import math
import random
from aes import AESCrypto
import re
import qrcode
import pyzbar.pyzbar as pyzbar
from PIL import Image,ImageEnhance

import platform
if platform.system() != "Linux":
    from moviepy.editor import *
    import cv2



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
    
    def encryptFile(self, filename, key, outFormat, table=[]):
        try:
            with open (filename, 'rb') as pf:
                message=pf.read()
                message = AESCrypto(key, b'0000000000000000').encrypt(message)

                if outFormat=='qr':
                    timeStr=datetime.datetime.now().strftime("%Y%m%d%H%M")
                    
                    #将base64编码的数据转化为二维码                
                    message=base64.b64encode(message)
                    tempIndex=0
                    partLen=200
                    outInfo=[]
                    while True:
                        if len(message[tempIndex*partLen : (tempIndex+1)*partLen]):
                            newImgFile='%03d.png' % tempIndex
                            if os.path.isfile(newImgFile):
                                os.remove(newImgFile)
                            
                            img = qrcode.make((timeStr+'#%03d' % tempIndex).encode("utf-8")+message[tempIndex*partLen : (tempIndex+1)*partLen])
                            img.save(newImgFile)
                            outInfo.append(newImgFile)
                            print (newImgFile)
                            tempIndex+=1
                        else:
                            break
                
                    #将outInfo中这些新生成的文件，制作成视频
                    targetVideo = 'myCreateVideo.mp4'
                    fileNames=outInfo
                    fileNames+=[fileNames[-1]]*5
                    im1=cv2.imread(fileNames[0])
                    im2=cv2.imread(fileNames[-1])
                    im2=cv2.resize(im2, (im1.shape[0],im1.shape[1]))
                    cv2.imwrite(fileNames[-1], im2)
                    frames=[cv2.imread(item) for item in fileNames]
                    fps=1
                    video=ImageSequenceClip(frames,fps=fps)
                    video.write_videofile(targetVideo, fps=fps, codec='mpeg4')
                    
                    outInfo=','.join(outInfo)
                    message=outInfo
                elif outFormat=='b64':
                    #将信息转化为base64
                    message=base64.b64encode(message)
                elif outFormat=='chinese':
                    #将二进制数据转化为汉字
                    message = self.transData2Chinese(message, table)
                else:
                    assert 0
        except:
            print ('encrypt fail')
        
        return message

    def decryptFile(self, message, key, filename, outFormat, table=[]):
        print ("input info format is %s" % outFormat)
        if outFormat=='qr':
            message={}
            
            #call python2 script to get frame from video
            f=os.popen("python2 preReadVideo_py2.py")
            #read frame to memory
            files=f.readlines()[0].strip("\r\n").split(",")
            print (files)
            
            last_timeStr=""
            last_indexStr=""
            #for img in frames:
            for imgFileName in files:
                img=Image.open(imgFileName)
                #如果需要，这里调整亮度，对比度，锐度，灰度图等,有时也需要适当缩放
                img = img.convert("L")
                    
                #识别
                barcodes = pyzbar.decode(img)
                #print ("barcodes:",barcodes)
                for barcode in barcodes:
                    barcodeData = barcode.data.decode("utf-8")
                    try:
                        m=re.match(r'''[0-9]{12}#[0-9]{3}''',barcodeData[:16])#信息的前面是时间戳和编号（类似'201905071228#000'），共16位
                    except:
                        continue
                    if m:
                        timeStr=m.group(0)[:12]
                        indexStr=int(m.group(0)[13:])
                            
                        if last_timeStr != timeStr or last_indexStr != indexStr:
                            last_timeStr=timeStr
                            last_indexStr=indexStr
                            print ("timeStr:",timeStr,"\tindexStr:",indexStr)
                            if timeStr in message.keys():
                                message[timeStr].append([indexStr, barcodeData[16:]])
                            else:
                                message[timeStr]=[]
                                message[timeStr].append([indexStr, barcodeData[16:]])
                                pass
                            pass
                        pass
                    pass
                pass
            

            
            #这时message是类似{"201905071202": [[0, "abcde"], [1, "fghijkl"]], "201905071203": [[0, "mnopq"], [0, "mnopq"], [1, "rstuvw"]]}的形式
            #print (message)
            #取出有最新时间戳的数据
            message=message[sorted(list(message.keys()))[-1]]
            #这时message是类似[[0, 'mnopq'], [0, "mnopq"], [1, 'rstuvw']]的形式，要基于序号排序
            message.sort(key=lambda x:x[0])
            #取数据，注意要去重
            indexList=[item[0] for item in message]
            dataList=[item[1] for item in message]
            message=[]
            for i in range(max(indexList)+1):
                if i in indexList:
                    message.append(dataList[indexList.index(i)])
                else:
                    print ("Data with Index %d is miss!!!" % i)
            message="".join(message)
            print (message)
            message = base64.b64decode(message)            
            pass
        elif outFormat=='b64':
            message = base64.b64decode(message)
        elif outFormat=='chinese':
            #解码汉字为二进制数据
            message = self.transChinese2Data(message, table)
        else:
            assert 0
            
            
        message=AESCrypto(key, b'0000000000000000').decrypt(message)        
        try:
            with open (filename, 'wb') as pf:
                pf.write(message)
        except:
            print ('decrypt fail')
