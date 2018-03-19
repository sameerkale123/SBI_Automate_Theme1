# -*- coding: utf-8 -*-
"""
Image recognizer

This code detects, inserts and communicates when it find the HNI Customers
All repeated images are written on 1 table.
Unique records are saved in Time_Cam_ID_Img and HNI_Customers_Uniq tables

Code is tested and SMS/Emails are verified
Emails: Only contains text
"""
import cv2, os
import numpy as np
from PIL import Image
import pickle
import sqlite3
import datetime
import zerosms
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Initiate Training Data    
recognizer=cv2.createLBPHFaceRecognizer();
recognizer.load("dataTraining/trainingData.yml");
cascadePath = "D:/Desktop/Sameer/Analytics/31_Video Analytics/2. Face recognition/haarcascades/haarcascade_frontalface_default.xml"
faceCascade=cv2.CascadeClassifier(cascadePath);
path = 'dataSet';

# Clear Temp table
# Clear off the database for older video database
conn=sqlite3.connect("SqliteDataBase\\SBI_HNI_Customers.db")   
conn.execute("DELETE FROM Time_Cam_ID")
#conn.execute("DELETE FROM Time_Cam_ID_Distinct")
conn.execute("DELETE FROM Time_Cam_ID_Img")
conn.execute("DELETE FROM HNI_Cust_Uniq")                                       
#conn.execute("DELETE FROM HNI_Customers_Visits") 
conn.commit()
conn.close()

ID=0;

# Function to Get Profile from Data base as per Predicted ID - Repeats for No of Faces
def getProfile(ID,CamID):
    conn=sqlite3.connect("SqliteDataBase\\SBI_HNI_Customers.db")
    cmd1="SELECT * FROM HNI_Customers WHERE ID="+str(ID) # For Display purpose
    cursor1=conn.execute(cmd1)
    # Date-time variables
    profile=None

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S:%f")
    date_time=now.strftime("%Y-%m-%d %H:%M")
    #Image data
    picture_file = "dataCamImages_HNI/Pic_Cust"+str(ID)+".jpg"
    with open(picture_file, 'rb') as input_file:
        ablob=input_file.read()
        base=os.path.basename(picture_file)
        afile, ext = os.path.splitext(base)
        fname = afile+ext
        image=sqlite3.Binary(ablob)
        
    for row1 in cursor1:    #Scan Customer database
        profile=row1
        Name=row1[1]
        Mobile=row1[2]
        Status=row1[3]
        Misc=row1[4]
        print "---------------"
        print "Time = ", time
        print "ID = ", ID
        print "NAME = ", row1[1], "\n"
        conn.execute("INSERT INTO Time_Cam_ID(CamID,ID,Image,Filename,Date,Time) VALUES('10001',?,?,?,?,?)",(ID,image,fname,date,time))

        # Find Unique
        cursor2=conn.execute('''SELECT CamID, ID, Date, Time FROM Time_Cam_ID_Img WHERE ID=? ''',(ID,))
        cursor3=conn.execute('''SELECT CamID, ID, Date, Time FROM HNI_Cust_Uniq WHERE ID=? ''',(ID,))
        cursor4=conn.execute("SELECT * FROM Cam_Branch_Manager WHERE CamID='10001'")
        isRecordExistImg=0
        isRecordExistUniq=0
        for row2 in cursor2:    #Scan Img database
            isRecordExistImg=1
        for row3 in cursor3:    #Scan Uniq database
            isRecordExistUniq=1
        for row4 in cursor4:    #Scan Branch Manager database
            IPAdd=row4[1]
            BranchID=row4[2]
            WMName=row4[3]
            WMEmail=row4[4]
            WMMobile=row4[5]
            print "BranchID =", row4[2]
            print "WMName=",row4[3]
        if(isRecordExistImg==0 and isRecordExistUniq==0):
            conn.execute("INSERT INTO Time_Cam_ID_Img(CamID,ID,Image,Filename,Date,Time) VALUES('10001',?,?,?,?,?)",(ID,image,fname,date,time))
            conn.commit()
            print "~~Inserted Record ID in Img=", ID
            print "~~Inserted Record ID in Img at Time=", time
            conn.execute("INSERT INTO HNI_Cust_Uniq(Date,Time,ID,Image,Filename,Name,Mobile, \
                Status,Misc,CamID,BranchID,Wealth_Manager_Name,Wealth_Manager_Email,Wealth_Manager_Mobile) \
                VALUES(?,?,?,?,?,?,?,?,?,'10001',?,?,?,?)",(date,time,ID,image,fname,Name,Mobile,Status,Misc,BranchID,WMName,WMEmail,WMMobile))
            conn.commit()
            print "~~Inserted Record ID in Uniq=", ID
            print "~~Inserted Record ID in Uniq at Time=", time
            print "====Send SMS and Email======="      
        elif(isRecordExistImg==1 and isRecordExistUniq==1):
            print "Record Exists ID=", ID
            print "~~Updated Record ID in Img=", ID
            print "~~Updated Record ID in Img at Time=", time
            conn.execute('''UPDATE Time_Cam_ID_Img SET CamID='10001',ID=?,Image=?,Filename=?,Date=?,Time=?\
                WHERE ID = ?''',(ID,image,fname,date,time,ID))
            conn.commit()
            conn.execute('''UPDATE HNI_Cust_Uniq SET Date=?,Time=?,ID=?,Image=?,Filename=?,Name=?,Mobile=?,Status=?,\
                Misc=?,CamID='10001',BranchID=?,Wealth_Manager_Name=?,Wealth_Manager_Email=?,Wealth_Manager_Mobile=?\
                WHERE ID = ?''',(date,time,ID,image,fname,Name,Mobile,Status,Misc,BranchID,WMName,WMEmail,WMMobile,ID))
            conn.commit()
            print "~~Updated Record ID in Uniq=", ID
            print "~~Updated Record ID in Uniq at Time=", time
        if(isRecordExistImg==0 and isRecordExistUniq==0):
            alertProfile(ID)
    conn.commit()
    return profile

# Function to Save the Customer Image & Write the Customer information in a new Database for Communication - Runs One Time
#def sendProfile(ID):
#    conn=sqlite3.connect("SqliteDataBase\\SBI_HNI_Customers.db")
#    conn.execute("INSERT INTO HNI_Cust_Uniq(Date,Time,ID,Image,Filename,Name,Mobile, \
#        Status,Misc,CamID,BranchID,Wealth_Manager_Name,Wealth_Manager_Email,Wealth_Manager_Mobile) \
#        SELECT Date,Time,U.ID,U.Image,Filename,Name,Mobile,Status,C.Misc,U.CamID,BranchID,Wealth_Manager_Name,\
#        Wealth_Manager_Email,Wealth_Manager_Mobile FROM Time_Cam_ID_Img U JOIN HNI_Customers AS C JOIN Cam_Branch_Manager B\
#        ON U.ID = C.ID AND U.CamID = B.CamID")
#    conn.execute("INSERT INTO HNI_Customers_Visits(Date,Time,ID,Image,Filename,Name,Mobile,Status,Misc,CamID,BranchID,Wealth_Manager_Name,Wealth_Manager_Email,Wealth_Manager_Mobile) \
#         SELECT Date,Time,U.ID,U.Image,Filename,Name,Mobile,Status,C.Misc,U.CamID,BranchID,Wealth_Manager_Name,Wealth_Manager_Email,Wealth_Manager_Mobile FROM Time_Cam_ID_Img U JOIN HNI_Customers AS C JOIN Cam_Branch_Manager B ON U.ID = C.ID AND U.CamID = B.CamID")
#    conn.commit()
#    conn.close()

# Function to send Plain Email
def send_email(user, pwd, recipient, subject, body):
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body
   # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.quit()
        print 'Successfully sent the e-mail'
    except:
        print "Failed to send mail"

# Function to send Email with Image Attachement
def send_email2(ID, user, pwd, recipient,subject,body):
    
    picture_file = "dataCamImages_HNI/Pic_Cust"+str(ID)+".jpg"
    img_data = open(picture_file, 'rb').read()
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = recipient
    msg['Subject'] = subject
    
    text = MIMEText(body)
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(picture_file))
    msg.attach(image)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(user, pwd)
    s.sendmail(user, recipient, msg.as_string())
    s.quit()
    print 'Successfully sent email with attachment'

# Function to Send Alert to the Branch Wealth Manager along with the Customer information - Runs One Time
def alertProfile(ID):
    index = 0;
    conn=sqlite3.connect("SqliteDataBase\\SBI_HNI_Customers.db")
#    SMScnt = conn.execute("SELECT COUNT(*) FROM HNI_Cust_Uniq")
    #for index in SMScnt:
    cmd5="SELECT * FROM HNI_Cust_Uniq WHERE ID="+str(ID)
    cursor5=conn.execute(cmd5)
    data=None
    for row5 in cursor5:
        data=row5
        Date=row5[0]
        Time=row5[1]
        Arrival_Time=Time[:5]
        CName=row5[5]
        CMobile=row5[6]
        Branch=row5[10]
        WMName=row5[11]
        WMEmail=row5[12]
        WMMobile=row5[13]
        print "CNAME = ", row5[5]
        print "WMNAME = ", row5[11], "\n"
#Way2SMS
        zerosms.sms(phno='8446992886',passwd='numb984sure084',message="Dear %s, SBI HNI Customer %s is in your branch" %(WMName,CName),receivernum=str(WMMobile))
        print "SMS Sent on Mobile"
#Email Notification
#        send_email(user     = 'smk.byod@gmail.com',
#                   pwd      = 'numb984sure084',
#                   recipient= [WMEmail],
#                   subject  = '**Alert: HNI Customer in Branch %s' %(Branch),
#                   body     = "Dear %s,\nSBI HNI Customer %s has arrived in your branch at %s.\nYou can contact them on Mobile No:%s.\n \nThanks & regards,\nNextGen Alert" %(WMName,CName,Arrival_Time,CMobile))

#Email notification with Image Attachment
        send_email2(ID,
                    user     = '@gmail.com',
                    pwd      = '',
                    recipient= '%s' %(WMEmail),
                    subject  = '**Alert: HNI Customer in Branch %s' %(Branch),
                    body     = "Dear %s,\nSBI HNI Customer %s has arrived in your branch at %s.\nYou can contact them on Mobile No:%s.\n \nThanks & regards,\nNextGen Alert" %(WMName,CName,Arrival_Time,CMobile))

# Actual Program to detect from Live Camera Feed
cam=cv2.VideoCapture(0);
CamID='10001'
font=cv2.cv.InitFont(cv2.cv.CV_FONT_HERSHEY_SIMPLEX,1,1,0,2)
while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,1.3,5)
    for(x,y,w,h) in faces:
        ID,conf=recognizer.predict(gray[y:y+h,x:x+w])
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,225,0), 2)
        profile=getProfile(ID,CamID)
        if(profile!=None):
            cv2.cv.PutText(cv2.cv.fromarray(img),str(profile[1]),(x,y+h+30),font,255);
            cv2.cv.PutText(cv2.cv.fromarray(img),str(profile[2]),(x,y+h+60),font,255);
            cv2.cv.PutText(cv2.cv.fromarray(img),str(profile[3]),(x,y+h+90),font,255);
            cv2.cv.PutText(cv2.cv.fromarray(img),str(profile[4]),(x,y+h+120),font,255);
            cv2.imwrite("dataCamImages_HNI\\Pic_Cust%d.jpg" % ID, img)     
              
        elif(profile==None):
            text = "Unknown"
            cv2.cv.PutText(cv2.cv.fromarray(img),str(text),(x,y+h+30),font,255);
            cv2.imwrite("dataCamImages_HNI\\Pic_Cust_Unknown.jpg", img)
    cv2.imshow("Face Recognizer",img);
    if((cv2.waitKey(1) & 0xff) ==ord('q')):
        break;
cam.release()
cv2.destroyAllWindows()


