import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSlider, QProgressBar
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from skimage.morphology import skeletonize, medial_axis
from skimage.util import img_as_ubyte
from PIL import Image


class ImageViewer(QMainWindow):
    def __init__(self, image_folder):
        super().__init__()
        self.image_folder = image_folder
        self.image_files = [f for f in os.listdir(image_folder)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        if not self.image_files:
            raise Exception("No images found in the specified folder")

        self.current_index = 0
        self.original_img = None
        self.binary_img = None
        self.initUI()
        self.loadImage()

    def initUI(self):
        self.setWindowTitle('')
        self.setGeometry(100, 100, 1200, 1000)  # Adjusted size for 2x2 layout

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create 2x2 grid layout for images
        grid_layout = QVBoxLayout()
        top_row = QHBoxLayout()
        bottom_row = QHBoxLayout()

        # Create slider for dilation control
        self.dilation_slider = QSlider(Qt.Horizontal)
        self.dilation_slider.setMinimum(0)
        self.dilation_slider.setMaximum(20)
        self.dilation_slider.setValue(0)
        self.dilation_slider.setTickPosition(QSlider.TicksBelow)
        self.dilation_slider.setTickInterval(1)
        self.dilation_slider.valueChanged.connect(self.onSliderValueChanged)

        slider_label = QLabel('Dilation Kernel Size:')
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.dilation_slider)

        # Image labels
        self.original_label = QLabel()
        self.dilated_label = QLabel()
        self.skeleton_label = QLabel()
        self.medial_axis_label = QLabel()

        top_row.addWidget(self.original_label)
        top_row.addWidget(self.dilated_label)
        bottom_row.addWidget(self.skeleton_label)
        bottom_row.addWidget(self.medial_axis_label)

        grid_layout.addLayout(top_row)
        grid_layout.addLayout(bottom_row)

        # Set minimum size for all labels
        for label in [self.original_label, self.dilated_label, self.skeleton_label, self.medial_axis_label]:
            label.setMinimumSize(500, 400)

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(self.image_files) - 1)
        self.progress_bar.setValue(0)

        main_layout.addLayout(slider_layout)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.progress_bar)

    def loadImage(self):
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])

        try:
            pil_image = Image.open(image_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            self.original_img = np.array(pil_image)
            self.original_img = cv2.cvtColor(self.original_img, cv2.COLOR_RGB2BGR)

            # Create binary image
            gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
            _, self.binary_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            self.setWindowTitle(f'{self.image_files[self.current_index]}')
            self.updateDisplay()

            # Update progress bar
            self.progress_bar.setValue(self.current_index)
        except Exception as e:
            print(f"Failed to load image: {image_path}")
            print(f"Error: {str(e)}")

    def createQImage(self, img):
        height, width = img.shape[:2]
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * width
            return QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888).copy()
        else:
            return QImage(img.data, width, height, width, QImage.Format_Grayscale8).copy()

    def onSliderValueChanged(self):
        self.updateDisplay()

    def updateDisplay(self):
        if self.original_img is None or self.binary_img is None:
            return

        # Get current dilation value
        kernel_size = self.dilation_slider.value()

        # Create dilated image
        if kernel_size > 0:
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            dilated = cv2.dilate(self.binary_img, kernel, iterations=1)
        else:
            dilated = self.binary_img.copy()

        # Create skeleton
        skeleton = skeletonize(dilated > 0)
        skeleton_img = img_as_ubyte(skeleton)

        # Create medial axis and distance transform
        skel, distance = medial_axis(dilated > 0, return_distance=True)

        # Normalize the distance
        distance_on_skel = distance * skel
        distance_on_skel = (distance_on_skel - distance_on_skel.min()) / (
            distance_on_skel.max() - distance_on_skel.min())

        # Create a custom colormap similar to 'magma'
        colors = ['#000003', '#3B0F6F', '#8C2981', '#DD4968', '#FD9F6C', '#FBFCBF']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('custom_magma', colors, N=n_bins)

        # Apply colormap to distance transform
        colored_distance = cmap(distance_on_skel)
        colored_distance = img_as_ubyte(colored_distance)

        # Add contour
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(colored_distance, contours, -1, (255, 255, 255, 255), 1)

        # Convert to QImage
        original_qimage = self.createQImage(self.original_img)
        dilated_qimage = self.createQImage(dilated)
        skeleton_qimage = self.createQImage(skeleton_img)
        medial_axis_qimage = self.createQImage(colored_distance)

        # Create and scale pixmaps
        for qimage, label in [
            (original_qimage, self.original_label),
            (dilated_qimage, self.dilated_label),
            (skeleton_qimage, self.skeleton_label),
            (medial_axis_qimage, self.medial_axis_label)
        ]:
            pixmap = QPixmap.fromImage(qimage)
            pixmap = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)

    def wheelEvent(self, event):
        try:
            delta = event.angleDelta().y()

            # Store old index in case we need to revert
            old_index = self.current_index

            if delta > 0:
                self.current_index = (self.current_index - 1) % len(self.image_files)
            else:
                self.current_index = (self.current_index + 1) % len(self.image_files)

            # Try to load new image
            try:
                self.loadImage()
            except Exception:
                print(f"Failed to load image at index {self.current_index}, reverting...")
                self.current_index = old_index
                self.loadImage()

        except Exception as e:
            print(f"Error in wheel event: {str(e)}")
            # Safely ignore the event if something goes wrong


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Replace with your MPEG-7 dataset folder path
    image_folder = "E:\\Datasets\\MPEG7_CE-Shape-1_Part_B"

    viewer = ImageViewer(image_folder)
    viewer.show()
    sys.exit(app.exec_())
