# -*- coding: utf-8 -*-
"""
Objective:
1. Detect faces from webcam
2. Ask User to enter the ID for the face
3. Capture the faces and store the Images (captured in 10 milli secs) and name file as ID
4. Output is stored in folder: dataSet/
Create
"""
import cv2
import numpy as np
# cv2.__file__


faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml');
cam=cv2.VideoCapture(0);
id = raw_input('Enter User ID:')
sampleNum=0;
while (True):
    ret, img = cam.read();
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    for(x,y,w,h) in faces:
        sampleNum=sampleNum+1;
        cv2.imwrite("dataSet/User."+str(id)+"."+str(sampleNum)+".jpg",gray[y:y+h,x:x+h])
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0), 2)
        cv2.waitKey(10);
    cv2.imshow("Face",img);
    cv2.waitKey(1);
    if(sampleNum>10):
        break
cam.release()
cv2.destroyAllWindows()
