import numpy as np
import cv2


def color_check():
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Trackbars")
    trackbar_names = ["L - H", "L - S", "L - V", "U - H", "U - S", "U - V"]
    default_values = [0, 0, 0, 179, 255, 255]

    for name, default_value in zip(trackbar_names, default_values):
        cv2.createTrackbar(
            name, "Trackbars", default_value, 255 if "S" in name else 179, nothing
        )

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_blue = np.array(
            [cv2.getTrackbarPos(name, "Trackbars") for name in trackbar_names[:3]]
        )
        upper_blue = np.array(
            [cv2.getTrackbarPos(name, "Trackbars") for name in trackbar_names[3:]]
        )
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # show thresholded image
        cv2.imshow("mask", mask)
        cv2.imshow("result", result)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    return lower_blue, upper_blue


def nothing(x):
    pass


if __name__ == "__main__":
    lower_blue, upper_blue = color_check()
    print("Lower Blue:", lower_blue)
    print("Upper Blue:", upper_blue)
