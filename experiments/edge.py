from cursor import data
from cursor import device
from cursor import path
from cursor import renderer

import cv2
import numpy as np
import matplotlib.pyplot as plt


def callback(x):
    print(x)


def detect_edge(image):
    """Detecting Edges"""
    image_with_edges = cv2.Canny(image, 30, 200)
    images = [image, image_with_edges]
    location = [121, 122]
    for loc, img in zip(location, images):
        plt.subplot(loc)
        plt.imshow(img, cmap="gray")
    plt.savefig("edge.png")
    plt.show()


def canny():

    canny = cv2.Canny(image, 85, 255)

    cv2.namedWindow("image")  # make a window with name 'image'
    # cv2.createTrackbar('L', 'image', 0, 255, callback)  # lower threshold trackbar for window 'image
    # cv2.createTrackbar('U', 'image', 0, 255, callback)  # upper threshold trackbar for window 'image

    while 1:
        numpy_horizontal_concat = np.concatenate(
            (image, canny), axis=1
        )  # to display image side by side
        cv2.imshow("image", numpy_horizontal_concat)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # escape key
            break
        l = 18  # cv2.getTrackbarPos('L', 'image')
        u = 3  # cv2.getTrackbarPos('U', 'image')

        canny = cv2.Canny(image, l, u)

    cv2.destroyAllWindows()


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


def save_contours(con):
    pc = path.PathCollection()
    for contour in con:
        p = path.Path()
        first = contour[0][0]
        last = contour[-1][0]
        p.add(first[0], first[1])
        for point in contour:
            p.add(point[0][0], point[0][1])
        # print(contours)
        p.add(last[0], last[1])
        pc.add(p)
    return pc


def test():
    global image
    image = cv2.imread("1304_small.jpg", 0)

    cv2.namedWindow("image")  # make a window with name 'image'
    cv2.createTrackbar(
        "L", "image", 0, 255, callback
    )  # lower threshold trackbar for window 'image
    # cv2.createTrackbar('U', 'image', 0, 255, callback)  # upper threshold trackbar for window 'image

    while 1:
        # numpy_horizontal_concat = np.concatenate((image, canny), axis=1)  # to display image side by side
        l = cv2.getTrackbarPos("L", "image")
        # u = cv2.getTrackbarPos('U', 'image')

        image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, l, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        # draw all contours
        image_c = cv2.drawContours(binary, contours, -1, (0, 255, 0), 2)
        cv2.imshow("image", binary)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # escape key
            break
        if k == 115:
            print("saving")
            pc = save_contours(contours)

            pc.reorder_quadrants(10, 10)

            device.SimpleExportWrapper().ex(
                pc,
                device.PlotterType.ROLAND_DPX3300,
                device.PaperSize.LANDSCAPE_A1,
                15,
                "edge",
                f"edge{pc.hash()}",
            )


def save():
    image = cv2.imread("13042_small.jpg", 0)
    image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 134, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    pc = save_contours(contours)

    pc.reorder_quadrants(10, 10)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        15,
        "edge",
        f"edge{pc.hash()}",
    )


if __name__ == "__main__":
    save()
    # test()
    # show it
    # plt.imshow(image)
    # plt.show()
