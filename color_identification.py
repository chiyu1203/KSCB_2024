import numpy as np
import cv2
import json
from pathlib import Path


"""
Color identification: In this tutorial, we use colour-based tracking to identify objects of interest as this is an rather simple but robust (with limitation) method to demonstrate vision-based closed-loop experiments
The first step is isolate specific colour spectrum for your setup, so that you can use that parameters to track colour of interest.
Note: in this package, we use HSV colour space, instead of RGB colour space. Could you guess what would be the reason for that?

Practice: once you run this code, there will be 3 windows popping up, one for raw video, one for mask and the last one for colour threshold.
Adjust lower and upper bound of the HSV threshold with the mouse cursor to isolate color spectrum for the first colour
Once you start to tune these bounds, have a look on the mask window and see what is isolated.

Isolated color will be shown in the mask and result.
Press S to save the values of colour range.
Repeat the same procedure for the second colour.
Press Q to leave this procedure.

"""


def hsv_color_range():
    cap = cv2.VideoCapture(0)
    trackbar_title="Key S to save & Q to ESC"

    cv2.namedWindow(trackbar_title)
    trackbar_names = ["L - H", "L - S", "L - V", "U - H", "U - S", "U - V"]
    default_values = [0, 0, 0, 179, 255, 255]

    colour_profile = Path('color_ranges.json')
    colour_profile.unlink(missing_ok=True)

    for name, default_value in zip(trackbar_names, default_values):
        cv2.createTrackbar(
            name, trackbar_title, default_value, 179 if "H" in name else 255, nothing
        )

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_range = np.array(
            [cv2.getTrackbarPos(name, trackbar_title) for name in trackbar_names[:3]]
        )
        upper_range = np.array(
            [cv2.getTrackbarPos(name, trackbar_title) for name in trackbar_names[3:]]
        )
        mask = cv2.inRange(hsv, lower_range, upper_range)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # show thresholded image
        cv2.imshow("mask", mask)
        cv2.imshow("raw video + mask", result)

        key = cv2.waitKey(1)
        if key == ord("s"):
            # with open('color_ranges.csv', 'w', newline='') as csvfile:
            #     csvwriter = csv.writer(csvfile)
            #     csvwriter.writerow(["Lower H", "Lower S", "Lower V", "Upper H", "Upper S", "Upper V"])
            #     csvwriter.writerow(np.concatenate((lower_range, upper_range)))
            # color_ranges = {
            #     "lower_range": lower_range.tolist(),
            #     "upper_range": upper_range.tolist()
            # }
            color_ranges = {
                "lower_range": lower_range.tolist(),
                "upper_range": upper_range.tolist()
            }
            colour_profile = Path('color_ranges.json')
            if colour_profile.is_file():
                with open('color_ranges.json', 'r') as jsonfile:
                    data = json.load(jsonfile)
                    if not isinstance(data, list):
                        data = [data]
            else:
                data = []

            data.append(color_ranges)
            print(f"save colour profile {colour_profile} to json file")

            with open('color_ranges.json', 'w') as jsonfile:
                json.dump(data, jsonfile, indent=4)
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
