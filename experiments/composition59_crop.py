from cursor.path import Path, Spiral, PathCollection
from cursor import device

import composition59_data

data = composition59_data.data_map

import random
import cv2

def crop(fn):
    im = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    img = cv2.pyrDown(im)

    # threshold image
    ret, threshed_img = cv2.threshold(
        cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), 50, 255, cv2.THRESH_BINARY
    )

    thresh = cv2.dilate(threshed_img, None, iterations=4)
    thresh = cv2.erode(threshed_img, None, iterations=4)

    contours, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 5 and h > 10 and x > 10 and y > 10:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)

    cv2.imshow("contours", img)

    while cv2.waitKey() is not ord("q"):
        continue

    cv2.destroyAllWindows()


if __name__ == "__main__":

    selected = composition59_data.data_map[composition59_data.yellow][composition59_data.orange]
    crop(selected["file"])
    for k1, v1 in composition59_data.data_map.items():
        for k2, v2 in v1.items():
            print(k1 + " " +k2)
            if "1111" not in v2["file"]:
                crop(v2["file"])