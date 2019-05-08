# -*- coding: UTF-8 -*-
#python 2.7


import cv2
import json


vc=cv2.VideoCapture("../../data/qrvideo.mp4")
if vc.isOpened():
    lines=[]
    count=0
    while True:
        rval,frame=vc.read()
        count+=1
        if rval:
            if count%10==0:
                print ("%d" % count)
                cv2.imwrite("D:\\github\\data\\%03d.jpg" % count, frame)
        else:
            break
    vc.release()

