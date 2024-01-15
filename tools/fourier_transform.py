import time

import numpy as np
from matplotlib import pyplot as plt

import cv2  # opencv-based functions
import argparse  # process input arguments


def argparser():
    parser = argparse.ArgumentParser(
        description="""
            A demonstration program showing a live camera image feed
            alongside the intensity component of the Fourier transform
            of the camera image.\n
            Required: A python 2.7 installation (tested on Enthought Canopy),
            with: 
                - OpenCV (for camera reading)
                - numpy, TkAgg, matplotlib, scipy, argparse
            Cobbled together by Brian R. Pauw.
            Released under a GPLv3+ license.
            """
    )
    parser.add_argument(
        "-n",
        "--numShots",
        type=int,
        default=1e5,
        help="Max. number of images before program exit",
    )
    parser.add_argument(
        "-N", "--numBins", type=int, default=200, help="number of integration bins"
    )
    parser.add_argument(
        "-o",
        "--nContrIms",
        type=int,
        default=30,
        help="Calculate average contrast over N images",
    )
    parser.add_argument(
        "-d",
        "--camDevice",
        type=int,
        default=0,
        help="Integer specifying the camera device to use",
    )
    parser.add_argument(
        "-i",
        "--imAvgs",
        type=int,
        default=1,
        help="use an average of N images to show and FFT",
    )
    parser.add_argument(
        "-y",
        "--vScale",
        type=float,
        default=1.0,
        help="rescale the video vertically using interpolation",
    )
    parser.add_argument(
        "-x",
        "--hScale",
        type=float,
        default=1.0,
        help="rescale video horizontally using interpolation",
    )
    # image freezes when not downscaled in color!
    parser.add_argument(
        "-p",
        "--downScale",  # default = True,
        action="store_true",
        help="use pyramidal downscaling (once) on the image",
    )
    parser.add_argument(
        "-k",
        "--killCenterLines",
        action="store_true",
        help="remove central lines from the FFT image",
    )
    parser.add_argument(
        "-f", "--figid", type=str, default="liveFFT", help="name of the image window"
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default="400",
        help="use only centre N rows of video image",
    )
    parser.add_argument(
        "-c",
        "--columns",
        type=int,
        default="400",
        help="use only centre N columne of video image",
    )
    parser.add_argument(
        "-z",
        "--minContrast",
        type=float,
        default=7,
        help="minimum contrast scaling (adjusts black level)",
    )
    parser.add_argument(
        "-a",
        "--maxContrast",
        type=float,
        default=1,
        help="maximum contrast scaling (adjusts white level)",
    )
    parser.add_argument(
        "-q", "--color", action="store_true", help="trade a little speed for color"
    )

    return parser.parse_args()


class live_FT2(object):
    """
    This function shows the live Fourier transform of a continuous stream of
    images captured from an attached camera.

    """

    # internal variables and constants:
    color = False
    imMin = 0.004  # minimum allowed value of any pixel of the captured image
    contrast = np.concatenate(
        (np.zeros((10, 1)), np.ones((10, 1))), axis=1
    )  # internal use.

    def __init__(self, **kwargs):
        # process kwargs:
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

        self.vc = cv2.VideoCapture(self.camDevice)  # camera device
        cv2.namedWindow(self.figid, 0)  # 0 makes it work a bit better
        cv2.resizeWindow(self.figid, 1024, 768)  # this doesn't keep
        # raw_input('Press Enter to start') #wait
        # start image collection, very device specific here.
        rval, frame = self.vc.read()
        # we need to wait a bit before we get decent images
        print("warming up camera... (.1s)")
        time.sleep(0.1)
        rval = self.vc.grab()
        rval, frame = self.vc.retrieve()
        # determine if we are not asking too much
        frameShape = np.shape(frame)
        if self.rows > frameShape[1]:
            self.rows = frameShape[1]
        if self.columns > frameShape[0]:
            self.columns = frameShape[0]

        # calculate crop
        self.vCrop = np.array(
            [
                np.ceil(frameShape[0] / 2.0 - self.columns / 2.0),
                np.floor(frameShape[0] / 2.0 + self.columns / 2.0),
            ],
            dtype=int,
        )
        self.hCrop = np.array(
            [
                np.ceil(frameShape[1] / 2.0 - self.rows / 2.0),
                np.floor(frameShape[1] / 2.0 + self.rows / 2.0),
            ],
            dtype=int,
        )
        # start image cleanup with something like this:
        # for a running contrast of nContrIms frames
        self.contrast = np.concatenate(
            (np.zeros((self.nContrIms, 1)), np.ones((self.nContrIms, 1))), axis=1
        )

        # prepare for plotting integrated graph
        [xsize, ysize] = [self.columns, self.rows]
        xc = np.linspace(-xsize / 2.0, xsize / 2.0, xsize)
        yc = np.linspace(-ysize / 2.0, ysize / 2.0, ysize)
        self.binEdges = np.linspace(0.01, 1, self.numBins + 1)
        dist = np.sqrt(np.add.outer(xc**2, yc**2))
        self.pixelDist = dist / dist.max()
        # y, xEdges = np.histogram(dist, weights = a, bins = binEdges, density = True)

        self.pltFig = plt.figure(figsize=[8, 4])
        self.pltAx = self.pltFig.add_axes(
            [0, 0, 1, 1], frameon=False, facecolor="g", yscale="log"
        )
        self.pltAx.set_autoscaley_on(False)
        self.pltAx.set_xlim(0.0, 0.7)
        self.pltAx.set_ylim(0.1, 1)
        self.pltAx.grid("on")
        (self.pltLine,) = self.pltAx.plot([], [], ".-")
        self.pltFig.show()

        Nr = 0
        # main loop
        while Nr <= self.numShots:
            a = time.time()
            Nr += 1
            contrast = self.camimage_ft()
            print("framerate = {} fps \r".format(1.0 / (time.time() - a)))
        # stop camera
        self.vc.release()

    def camimage_ft(self):
        imAvgs = self.imAvgs
        vCrop = self.vCrop
        hCrop = self.hCrop
        contrast = self.contrast

        # read image
        rval = self.vc.grab()
        rval, im = self.vc.retrieve()
        im = np.array(im, dtype=float)
        # if we want to use an average of multiple images:
        if imAvgs > 1:
            im /= float(imAvgs)
            for imi in np.arange(2, imAvgs + 1):
                dummy, aim = self.vc.read()
                im += aim / float(imAvgs)

                # crop image
        im = im[vCrop[0] : vCrop[1], hCrop[0] : hCrop[1], :]
        # scaling horizontal axis down
        if (self.vScale != 1) or (self.hScale != 1):
            im = cv2.resize(im, None, fx=self.hScale, fy=self.vScale)
        # pyramid downscaling
        # if self.downScale or self.color: #color image freezes when not downscaled!
        if self.downScale:  # large and color images freeze when not downscaled!
            im = cv2.pyrDown(im)

        if not self.color:
            # reduce dimensionality
            im = np.mean(im, axis=2, dtype=float)
        # make sure we have no zeros
        im = (im - im.min()) / (im.max() - im.min())
        im = np.maximum(im, self.imMin)
        # FFT hints from http://www.astrobetter.com/fourier-transforms-of-images-in-python/
        # Numpy option, not quite all that much slower but much clearer than openCV
        if self.color:
            Intensity = np.zeros(np.shape(im))
            for ci in range(np.size(im, 2)):
                Intensity[:, :, ci] = (
                    np.abs(np.fft.fftshift(np.fft.fft2(im[:, :, ci]))) ** 2
                )
        else:
            Intensity = np.abs(np.fft.fftshift(np.fft.fft2(im))) ** 2

        # OpenCV option, http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_transforms/py_fourier_transform/py_fourier_transform.html#fourier-transform
        # dft = cv2.dft( np.float32(im), flags = cv2.DFT_COMPLEX_OUTPUT)
        # dft = np.fft.fftshift(dft)
        # Intensity = cv2.magnitude(dft[:, :, 0], dft[:, :, 1])
        # Intensity = abs(dft[:, :, 0])**2
        Intensity += self.imMin

        if self.killCenterLines:
            # blatantly copied from Samuel Tardif's code
            # kill the center lines for higher dynamic range
            # by copying the next row/column
            if not self.color:
                h, w = np.shape(Intensity)
                Intensity[int(h / 2 - 1) : int(h / 2 + 1), :] = Intensity[
                    int(h / 2 + 1) : int(h / 2 + 3), :
                ]
                Intensity[:, int(w / 2 - 1) : int(w / 2 + 1)] = Intensity[
                    :, int(w / 2 + 1) : int(w / 2 + 3)
                ]
            else:
                h, w, c = np.shape(Intensity)
                Intensity[int(h / 2 - 1) : int(h / 2 + 1), :, :] = Intensity[ int(h / 2 + 1) : int(h / 2 + 3), :, : ]
                Intensity[:, int(w / 2 - 1) : int(w / 2 + 1), :] = Intensity[
                    :, int(w / 2 + 1) : int(w / 2 + 3), :
                ]

        # running average of contrast
        # circshift contrast matrix up
        contrast = contrast[
            np.arange(1, np.size(contrast, 0) + 1) % np.size(contrast, 0), :
        ]
        # replace bottom values with new values for minimum and maximum
        contrast[-1, :] = [np.min(Intensity), np.max(Intensity)]

        # openCV draw
        vmin = np.log(contrast[:, 0].mean()) + self.minContrast
        vmax = np.log(contrast[:, 1].mean()) - self.maxContrast
        # print('{}'.format(Intensity.dtype)) float32
        Intensity = (np.log(Intensity + self.imMin) - vmin) / (vmax - vmin)
        Intensity = Intensity.clip(0.0, 1.0)
        # Intensity = (Intensity - Intensity.min()) / (Intensity.max() - Intensity.min())

        time.sleep(0.01)
        cv2.imshow(self.figid, np.concatenate((im, Intensity), axis=1))

        #         y, xEdges = np.histogram(self.pixelDist,
        #             weights = Intensity,
        #             bins = self.binEdges,
        #             density = True)
        y = (
            np.histogram(
                self.pixelDist,
                weights=Intensity,
                bins=self.binEdges,
            )[0]
            / np.histogram(self.pixelDist, bins=self.binEdges)[0]
        )

        # self.pltAx.clear()
        self.pltLine.set_xdata(np.cumsum(np.diff(self.binEdges)))
        self.pltLine.set_ydata(y)
        self.pltAx.relim()
        self.pltAx.autoscale_view()
        # draw *and* flush
        self.pltFig.canvas.draw()
        # self.pltFig.canvas.flush_events()

        # self.pltAx.plot(np.cumsum(np.diff(xEdges)), y, ".-")
        # self.pltAx.axis("auto")
        # self.pltAx.redraw_in_frame()

        # self.pltFig.show()
        # cv2.updateWindow(figid)

        # cv2.imwrite(r"temp.jpg",255 * np.concatenate((im, Intensity),axis = 1))

        cv2.waitKey(1)

        return contrast


if __name__ == "__main__":
    adict = argparser()
    # run the program, scotty! I want a kwargs object, so convert args:
    adict = vars(adict)
    live_FT2(**adict)  # and expand to kwargs
