import numpy as np
import cv2
'''
Color identification: use mouse cursor to adjust lower and upper bound of the threshold to isolate color spectrum. Isolated color will be shown in the mask and result. 
Press Q to save the result and leave this procedure
'''


def hsv_color_range():
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Trackbars")
    trackbar_names = ["L - H", "L - S", "L - V", "U - H", "U - S", "U - V"]
    default_values = [0, 0, 0, 179, 255, 255]

    for name, default_value in zip(trackbar_names, default_values):
        cv2.createTrackbar(
            name, "Trackbars", default_value, 179 if "H" in name else 255, nothing
        )

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_range = np.array(
            [cv2.getTrackbarPos(name, "Trackbars") for name in trackbar_names[:3]]
        )
        upper_range = np.array(
            [cv2.getTrackbarPos(name, "Trackbars") for name in trackbar_names[3:]]
        )
        mask = cv2.inRange(hsv, lower_range, upper_range)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # show thresholded image
        cv2.imshow("mask", mask)
        cv2.imshow("result", result)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    return lower_range, upper_range


def nothing(x):
    pass


if __name__ == "__main__":
    lower_range, upper_range = hsv_color_range()
    print("The lower bound of the threshold:", lower_range)
    print("The upper bound of the threshold:", upper_range)
