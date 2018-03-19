# -*- coding: utf-8 -*-
"""
Objective
1. Extract relative path of DataSet folder
2. Get all the image samples from the DataSet folder
3. Store the Face and its ID as an array of training data
4. Input Folder: dataSet
5. Output Folder: dataTraining/trainingData.yml
"""
import os
import cv2
import numpy as np
from PIL import Image

recognizer=cv2.createLBPHFaceRecognizer();
path='dataSet'

def getImagesWithID(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
#    print imagePaths
#getImagesWithID(path)
    faces=[]
    IDs=[]
    for imagePath in imagePaths:
        faceImg=Image.open(imagePath).convert('L');
        faceNp=np.array(faceImg,'uint8')
        ID=int(os.path.split(imagePath)[-1].split('.')[1])
        faces.append(faceNp)
        print ID
        IDs.append(ID)
        cv2.imshow("Training",faceNp)
        cv2.waitKey(10)
    return np.array(IDs), faces

IDs,faces=getImagesWithID(path)
recognizer.train(faces,np.array(IDs))
recognizer.save('dataTraining/trainingData.yml')
cv2.destroyAllWindows()

