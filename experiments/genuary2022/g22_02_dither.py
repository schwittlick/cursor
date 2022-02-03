from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter
from cursor import misc
from numpy import random

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import cv2


class ditherModule(object):
    def dither(self, img, method="floyd-steinberg", resize=False):
        if resize:
            img = cv2.resize(
                img,
                (np.int(0.5 * (np.shape(img)[1])), np.int(0.5 * (np.shape(img)[0]))),
            )
        if method == "simple2D":
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + (0.5 * err)
                    out[i + 1][j] = out[i + 1][j] + (0.5 * err)

            return out[1 : rows - 1, 1 : cols - 1]

        elif method == "floyd-steinberg":
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    # threshold step
                    if out[i][j] > 0.9:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + ((7 / 16) * err)
                    out[i + 1][j - 1] = out[i + 1][j - 1] + ((3 / 16) * err)
                    out[i + 1][j] = out[i + 1][j] + ((5 / 16) * err)
                    out[i + 1][j + 1] = out[i + 1][j + 1] + ((1 / 16) * err)

            return out[1 : rows - 1, 1 : cols - 1]

        elif method == "jarvis-judice-ninke":
            img = cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(2, rows - 2):
                for j in range(2, cols - 2):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + ((7 / 48) * err)
                    out[i][j + 2] = out[i][j + 2] + ((5 / 48) * err)

                    out[i + 1][j - 2] = out[i + 1][j - 2] + ((3 / 48) * err)
                    out[i + 1][j - 1] = out[i + 1][j - 1] + ((5 / 48) * err)
                    out[i + 1][j] = out[i + 1][j] + ((7 / 48) * err)
                    out[i + 1][j + 1] = out[i + 1][j + 1] + ((5 / 48) * err)
                    out[i + 1][j + 2] = out[i + 1][j + 2] + ((3 / 48) * err)

                    out[i + 2][j - 2] = out[i + 2][j - 2] + ((1 / 48) * err)
                    out[i + 2][j - 1] = out[i + 2][j - 1] + ((3 / 48) * err)
                    out[i + 2][j] = out[i + 2][j] + ((5 / 48) * err)
                    out[i + 2][j + 1] = out[i + 2][j + 1] + ((3 / 48) * err)
                    out[i + 2][j + 2] = out[i + 2][j + 2] + ((1 / 48) * err)

            return out[2 : rows - 2, 2 : cols - 2]

        else:
            raise TypeError(
                'specified method does not exist. available methods = "simple2D", "floyd-steinberg(default)", "jarvis-judice-ninke"'
            )


def fft(img):
    img_float32 = np.float32(img)

    dft = cv2.dft(img_float32, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)

    magnitude_spectrum = 20 * np.log(
        cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
    )

    plt.subplot(121), plt.imshow(img, cmap="gray")
    plt.title("Input Image"), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(magnitude_spectrum, cmap="gray")
    plt.title("Magnitude Spectrum"), plt.xticks([]), plt.yticks([])
    plt.show()


def fft2(img, outname):
    # https://scipy-lectures.org/intro/scipy/auto_examples/solutions/plot_fft_image_denoise.html
    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = 20 * np.log(
        cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
    )
    plt.subplot(121), plt.imshow(img, cmap="gray")
    plt.title("Input Image"), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(magnitude_spectrum, cmap="gray")
    plt.title("Magnitude Spectrum"), plt.xticks([]), plt.yticks([])
    plt.show()

    rows, cols = img.shape
    crow, ccol = rows / 2, cols / 2
    # create a mask first, center square is 1, remaining all zeros
    mask = np.zeros((rows, cols, 2), np.uint8)
    size = 3
    x1_start = int(crow - size)
    x1_end = int(crow + size)
    y_start = int(ccol - size)
    y_end = int(ccol + size)
    mask[x1_start:x1_end, y_start:y_end] = 1
    # apply mask and inverse DFT
    fshift = dft_shift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    plt.subplot(121), plt.imshow(img, cmap="gray")
    plt.title("Input Image2"), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(img_back, cmap="gray")
    plt.title("Magnitude Spectrum2"), plt.xticks([]), plt.yticks([])
    plt.show()
    return cv2.normalize(img_back.astype("float"), None, 0.0, 255.0, cv2.NORM_MINMAX)



def img_to_path(img, lines: int = 660):
    """
    This works only for A3 on HP7579a
    Mit dem neuen zentrierungs-Mechanismus haben wir 33cm in der Höhe
    Mit Stiftstärke von ~0.5mm -> 660 linien
    """
    pc = path.PathCollection()

    rows, cols = img.shape
    for x in range(rows):
        pa = path.Path()
        for i in range(lines):
            line_index = int(misc.map(i, 0, lines, 0, cols, True))
            k = img[x, line_index]
            if k == 0:
                pa.add(x, line_index)
                pa.add(x, line_index + 0.1)
                pass
            if k == 255:
                if pa.empty():
                    continue

                pa.pen_select = int(np.clip(len(pa), 0, 16) / 2)
                pc.add(pa)
                pa = path.Path()
                pass
    return pc


def g22_dither(img, outname):
    dither_object = ditherModule()
    out = dither_object.dither(img, "floyd-steinberg", False)
    # cv2.imshow('dithered image', out)
    out = cv2.normalize(out.astype("float"), None, 0.0, 255.0, cv2.NORM_MINMAX)
    cv2.imwrite(
        f"Z:\\dev\\cursor\\data\\experiments\\genuary22\\jpg\\{outname}.jpg", out
    )
    cv2.waitKey(0)


def dither_fin():
    """
    load image and dither with colors to hpgl
    """
    to_transform = cv2.imread(
        "Z:\\dev\\cursor\\data\\experiments\\genuary22\\jpg\\dithered5 (Small)_done.jpg",
        0,
    )
    pc = img_to_path(to_transform)

    sorter = filter.Sorter(param=filter.Sorter.PEN_SELECT, reverse=True)
    pc.sort(sorter)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_02_dither",
        "different_colors",
    )

if __name__ == "__main__":
    # to_dither = cv2.imread('Z:\\dev\\cursor\\data\\experiments\\genuary22\\jpg\\dithered5 (Small).jpg', 0)
    # g22_dither(to_dither, "dithered5 (Small)_done")
    img = cv2.imread('space1.jpg', 0)
    out = fft2(img, "dithered5")

    #cv2.imwrite(
    #    f"Z:\\dev\\cursor\\data\\experiments\\genuary22\\jpg\\dithered5.jpg", out
    #)
