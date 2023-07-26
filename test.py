import cv2
import numpy as np
from track import color_check
lower_blue, upper_blue = color_check()
print(lower_blue, upper_blue)
cap=cv2.VideoCapture(0)

lower_range_1=np.array(lower_blue)
upper_range_1=np.array(upper_blue)
lower_range_2=np.array([62,128,118])
upper_range_2=np.array([119,255,255])

def color(img,lr,ur):
    num_cnt = 0
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lr,ur)
    _,mask1=cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
    cnts,_=cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for c in cnts:
        x=600
        if cv2.contourArea(c)>x:
            num_cnt=num_cnt+1
            x,y,w,h=cv2.boundingRect(c)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,("DETECT"),(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    return num_cnt

def color1(img):
    num_cnt = 0
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_range_1,upper_range_1)
    _,mask1=cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
    cnts,_=cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for c in cnts:
        x=600
        if cv2.contourArea(c)>x:
            num_cnt=num_cnt+1
            x,y,w,h=cv2.boundingRect(c)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,("DETECT"),(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    return num_cnt

def color2(img):
    num_cnt = 0
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_range_2,upper_range_2)
    _,mask1=cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
    cnts,_=cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for c in cnts:
        x=600
        if cv2.contourArea(c)>x:
            num_cnt=num_cnt+1
            x,y,w,h=cv2.boundingRect(c)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,("DETECT"),(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    return num_cnt
while True:
    ret,frame=cap.read()
    frame=cv2.resize(frame,(640,480))
    num_1 = color(frame, lower_range_1, upper_range_1)
    num_2 = color(frame, lower_range_2, upper_range_2)
    #num_1=color1(frame)
    #num_2=color2(frame)
    print(num_1,num_2)

            
    cv2.imshow("FRAME",frame)
    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()