import cv2
import numpy as np
from collections import deque
# from track_chatGPT import color_check
# lower_blue, upper_blue = color_check()
# print(lower_blue, upper_blue)
# lower_red, upper_red = color_check()
# print(lower_red, upper_red)
# lower_ranges = [np.array(lower_blue), np.array(lower_red)]
# upper_ranges = [np.array(upper_blue), np.array(upper_blue)]
lower_ranges = [np.array([96, 91, 83]), np.array([ 0, 80,  0])]
upper_ranges = [np.array([158, 255, 179]), np.array([78, 255, 179])]
pts = deque(maxlen=32)
counter=0


cap = cv2.VideoCapture(0)


def color(img, lower_range, upper_range):
    num_cnt = 0
    area=0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    _, mask1 = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for c in cnts:
        x = 600
        if cv2.contourArea(c) > x:
            num_cnt += 1
            area += cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img, "DETECT", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )
    return num_cnt, area

def camera_controller2(area_1, area_2):
    darea_1,darea_2=0,0
    pts.appendleft((int(area_1), int(area_2)))
    #print(pts)

    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        # print(bool(pts[i] is None))
        if pts[i - 1] is None or pts[i] is None:
            continue
        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and pts[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
            darea_1 = pts[-10][0] - pts[i][0]
            darea_2 = pts[-10][1] - pts[i][1]
            print(darea_2)
    # if darea_1 > 0:
    #     print("area1 decreases")
    # elif darea_1 < 0:
    #     print("area1 increases")
    # else:
    #     print("area1 stay the same")

    # if darea_2 > 0:
    #     print("area2 decreases")
    # elif darea_2 < 0:
    #     print("area2 increases")
    # else:
    #     print("area2 stay the same")

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    num_1,area_1 = color(frame, lower_ranges[0], upper_ranges[0])
    num_2,area_2 = color(frame, lower_ranges[1], upper_ranges[1])
    #print(f"first color number{num_1}, area{area_1}")
    #print(f"first color number{num_2}, area{area_2}")
    camera_controller2(area_1, area_2)
    counter +=1
    cv2.imshow("FRAME", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
