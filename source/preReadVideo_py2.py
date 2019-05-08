# -*- coding: UTF-8 -*-
#python 2.7


import cv2
import json

count=0
vc=cv2.VideoCapture("../../data/qrvideo.mp4")
if vc.isOpened():
    lines=[]
    while True:
        rval,frame=vc.read()
        if rval:
            count+=1
            print ("%d" % count)
            #lines.append(json.dumps(frame.tolist()))
        else:
            break
    try:
        with open("../../data/qrframes.txt", "w") as pf:
            pf.writelines(lines)
    except:
        pass
    vc.release()

