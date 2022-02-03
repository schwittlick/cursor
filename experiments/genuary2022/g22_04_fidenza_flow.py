import cv2 as cv
import numpy as np

# The video feed is read in as
# a VideoCapture object
#cap = cv.VideoCapture("Z:\\Dropbox\\0_MARCELSCHWITTLICK\\Marcel Schwittlick Interview Lab of Misfits.mp4")

# ret = a boolean return value from
# getting the frame, first_frame = the
# first frame in the entire video sequence
#ret, first_frame = cap.read()

# Converts frame to grayscale because we
# only need the luminance channel for
# detecting edges - less computationally
# expensive

img1 = cv.imread('f-612.png')
img2 = cv.imread('f-849.png')
prev_gray = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

# Creates an image filled with zero
# intensities with the same dimensions
# as the frame
mask = np.zeros_like(img2)

# Sets image saturation to maximum
mask[..., 1] = 255


# ret = a boolean return value from getting
# the frame, frame = the current frame being
# projected in the video
#ret, frame = cap.read()

# Opens a new window and displays the input
# frame
cv.imshow("input", img1)

# Converts each frame to grayscale - we previously
# only converted the first frame to grayscale
gray1 = cv.cvtColor(img1, cv.COLOR_BGRA2GRAY)
gray2 = cv.cvtColor(img2, cv.COLOR_BGRA2GRAY)

# Calculates dense optical flow by Farneback method
flow = cv.calcOpticalFlowFarneback(gray1, gray2,
                                   None,
                                   0.5, 3, 15, 3, 5, 1.2, 0)

# Computes the magnitude and angle of the 2D vectors
magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])

# Sets image hue according to the optical flow
# direction
mask[..., 0] = angle * 180 / np.pi / 2

# Sets image value according to the optical flow
# magnitude (normalized)
mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)

# Converts HSV to RGB (BGR) color representation
rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)

# Opens a new window and displays the output frame
cv.imshow("dense optical flow", rgb)
cv.imwrite('fidenza_flow.jpg', rgb)
# Updates previous frame
#prev_gray = gray

# Frames are read by intervals of 1 millisecond. The
# programs breaks out of the while loop when the
# user presses the 'q' key
#if cv.waitKey(1) & 0xFF == ord('q'):
#    break

# The following frees up resources and
# closes all windows
#cap.release()
cv.destroyAllWindows()