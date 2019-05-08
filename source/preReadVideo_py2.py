# -*- coding: UTF-8 -*-
#python 2.7


import cv2
import json


vc=cv2.VideoCapture("../../data/qrvideo.mp4")
if vc.isOpened():
    lines=[]
    count=0
    nameCount=0
    outStr=[]
    while True:
        rval,frame=vc.read()
        count+=1
        if rval:
            if count%10==0:
                cv2.imwrite("../../data/%03d.jpg" % nameCount, frame)
                outStr.append("../../data/%03d.jpg" % nameCount)
                nameCount+=1
        else:
            break
    print (",".join(outStr))
    vc.release()

