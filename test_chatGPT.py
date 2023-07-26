import cv2
import numpy as np
# from track_chatGPT import color_check
# lower_blue, upper_blue = color_check()
# print(lower_blue, upper_blue)
# lower_red, upper_red = color_check()
# print(lower_red, upper_red)
# lower_ranges = [np.array(lower_blue), np.array(lower_red)]
# upper_ranges = [np.array(upper_blue), np.array(upper_blue)]
lower_ranges = [np.array([96, 91, 83]), np.array([ 0, 80,  0])]
upper_ranges = [np.array([158, 255, 179]), np.array([78, 255, 179])]

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


while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    num_1,area_1 = color(frame, lower_ranges[0], upper_ranges[0])
    num_2,area_2 = color(frame, lower_ranges[1], upper_ranges[1])
    print(f"first color number{num_1}, area{area_1}")
    print(f"first color number{num_2}, area{area_2}")

    cv2.imshow("FRAME", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
