from cursor.path import Path, Spiral, PathCollection
from cursor import device

import composition59_data

data = composition59_data.data_map

import random
import cv2
import pathlib

oriImage = None
cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
filename = None
offset = 100
id = 1111


def mouse_crop(event, x, y, flags, param):
    # grab references to the global variables
    global x_start, y_start, x_end, y_end, cropping
    # if the left mouse button was DOWN, start RECORDING
    # (x, y) coordinates and indicate that cropping is being
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        cropping = True
    # Mouse is Moving
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping == True:
            x_end, y_end = x, y
    # if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates
        x_end, y_end = x, y
        cropping = False  # cropping is finished
        refPoint = [(x_start, y_start), (x_end, y_end)]
        if len(refPoint) == 2:  # when two points were found
            a, b, c, d = x_start * 3, y_start * 3, x_end * 3, y_end * 3
            roi = oriImage[b:d, a:c]
            cv2.imshow("Cropped", roi)
            roi = oriImage[b - offset : d + offset, a - offset : c + offset]
            p = pathlib.Path(filename)
            t = f"Z:\\144\\cropped\\{id}.jpg"
            cv2.imwrite(t, roi)

            cropping = False


def crop_interactive(fn, _id):
    global filename
    filename = fn
    global id
    id = _id

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", mouse_crop)

    global oriImage
    oriImage = cv2.imread(fn, cv2.IMREAD_UNCHANGED)

    while True:
        i = cv2.resize(
            oriImage, (int(oriImage.shape[1] / 3.0), int(oriImage.shape[0] / 3.0))
        )
        cv2.imshow("image", i)
        if cv2.waitKey() is ord("q"):
            break

    cv2.destroyAllWindows()


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
    selected = composition59_data.data_map[composition59_data.yellow][
        composition59_data.orange
    ]
    crop_interactive(selected["file"], selected["objktid"])
    for k1, v1 in composition59_data.data_map.items():
        for k2, v2 in v1.items():
            print(k1 + " " + k2)
            if "1111" not in v2["file"]:
                crop_interactive(v2["file"], f"{k1}-{k2}")
