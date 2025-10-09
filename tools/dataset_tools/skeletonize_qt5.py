import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QSettings
import numpy as np
from skimage.morphology import skeletonize
from skimage.color import rgb2gray
from skimage.util import invert
import cv2
import os

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import PlotterType
from cursor.export import ExportWrapper
from cursor.timer import Timer

from skeletonize_lib import skeleton_to_vectors


class ScalableImageLabel(QLabel):
    def __init__(self, title=""):
        super().__init__(title)
        self.base_image = None
        self.setMinimumSize(500, 500)

    def setBaseImage(self, image):
        self.base_image = image
        self.updateImage()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.base_image is not None:
            self.updateImage()

    def updateImage(self):
        if self.base_image is None:
            return

        # Get the widget's current size
        w = self.width()
        h = self.height()

        # Get image dimensions
        img_h, img_w = self.base_image.shape[:2]

        # Calculate scaling factor while maintaining aspect ratio
        scale = min(w / img_w, h / img_h)
        new_width = int(img_w * scale)
        new_height = int(img_h * scale)

        # Resize image
        if len(self.base_image.shape) == 2:  # Grayscale
            display_image = cv2.cvtColor(self.base_image, cv2.COLOR_GRAY2RGB)
        else:
            display_image = self.base_image

        display_image = cv2.resize(display_image, (new_width, new_height), interpolation=cv2.INTER_NEAREST)

        # Convert to QImage
        bytes_per_line = 3 * new_width
        qt_image = QImage(display_image.data, new_width, new_height, bytes_per_line, QImage.Format_RGB888)

        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)


class ImageSkeletonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("skeletonize")
        self.setGeometry(100, 100, 1200, 600)

        # Add target dimensions as class attributes
        self.target_width = 126
        self.target_height = 174

        # Initialize settings
        self.settings = QSettings("ImageSkeletonApp", "ImageProcessing")
        self.last_folder = self.settings.value("last_folder", os.path.expanduser("~"))
        self.current_rotation = int(self.settings.value("rotation_angle", 0))

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create image display area using custom labels
        image_layout = QHBoxLayout()
        self.original_label = ScalableImageLabel("Original Image")
        self.skeleton_label = ScalableImageLabel("Skeleton Image")

        image_layout.addWidget(self.original_label)
        image_layout.addWidget(self.skeleton_label)
        layout.addLayout(image_layout)

        # Create buttons
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_image)
        self.process_button.setEnabled(False)

        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.process_button)
        layout.addLayout(button_layout)

        self.image = None
        self.original_unrotated = None
        self.processed_image = None

        # Add keyboard tracking
        self.setFocusPolicy(Qt.StrongFocus)

        # Restore window geometry if it exists
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R and self.image is not None:
            self.current_rotation = (self.current_rotation + 90) % 360
            self.settings.setValue("rotation_angle", self.current_rotation)
            self.rotate_and_update()
        elif event.key() == Qt.Key_V and self.processed_image is not None:
            self.vectorize_skeleton()
        elif event.key() == Qt.Key_L:
            self.load_image()

    def vectorize_skeleton(self):
        vector_paths = skeleton_to_vectors(self.processed_image, min_path_length=2)
        print("Vector paths:", vector_paths)

        coll = Collection.from_tuples(vector_paths)
        for path in coll:
            path.pen_select = 1

        wrapper = ExportWrapper(
            coll, PlotterType.HP_7550A_A4, 10, "datasets", f"skeletonize_{Timer.timestamp()}", keep_aspect_ratio=True
        )
        wrapper.fit()
        wrapper.ex()

        # Export scaled image
        if self.processed_image is not None:
            h, w = self.processed_image.shape[:2]
            target_w, target_h = (126, 174)  # Always use portrait dimensions

            # Rotate the image if it's in landscape
            if w > h:
                self.processed_image = cv2.rotate(self.processed_image, cv2.ROTATE_90_CLOCKWISE)

            # Resize the image
            resized_image = cv2.resize(self.processed_image, (target_w, target_h), interpolation=cv2.INTER_NEAREST)

            # Create a new black background image (inverted from white)
            background = np.zeros((target_h, target_w), dtype=np.uint8)

            # Calculate position to paste the resized image
            top = (target_h - resized_image.shape[0]) // 2
            left = (target_w - resized_image.shape[1]) // 2

            # Paste the inverted resized image onto the black background
            background[top : top + resized_image.shape[0], left : left + resized_image.shape[1]] = 255 - resized_image

            # Save the image
            folder = DataDirHandler().png("datasets")
            output_path = folder / f"skeletonize_scaled_{Timer.timestamp()}.png"
            cv2.imwrite(output_path.as_posix(), background)
            print(f"Scaled and inverted image saved to: {output_path}")

    def rotate_and_update(self):
        if self.original_unrotated is None:
            return

        # For 90-degree rotations, we can use cv2.rotate which maintains image quality
        if self.current_rotation == 90:
            self.image = cv2.rotate(self.original_unrotated, cv2.ROTATE_90_CLOCKWISE)
        elif self.current_rotation == 180:
            self.image = cv2.rotate(self.original_unrotated, cv2.ROTATE_180)
        elif self.current_rotation == 270:
            self.image = cv2.rotate(self.original_unrotated, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:  # 0 degrees
            self.image = self.original_unrotated.copy()

        # Update display
        self.original_label.setBaseImage(self.image)

        # Update processed image
        self.process_image()

    def closeEvent(self, event):
        # Save window geometry and rotation when closing
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("rotation_angle", self.current_rotation)
        super().closeEvent(event)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", self.last_folder, "Images (*.png *.xpm *.jpg *.bmp)"
        )

        if file_name:
            # Update and save the last used folder
            self.last_folder = os.path.dirname(os.path.abspath(file_name))
            self.settings.setValue("last_folder", self.last_folder)

            # Load image using OpenCV
            self.original_unrotated = cv2.imread(file_name)
            if self.original_unrotated is not None:
                # Convert BGR to RGB
                self.original_unrotated = cv2.cvtColor(self.original_unrotated, cv2.COLOR_BGR2RGB)

                # Print the original resolution of the loaded image
                height, width = self.original_unrotated.shape[:2]
                print(f"Original image resolution: {width}x{height}")

                # Determine target dimensions based on aspect ratio
                aspect_ratio = width / height
                if aspect_ratio > 1:  # Landscape
                    target_size = (174, 126)
                else:  # Portrait or square
                    target_size = (126, 174)

                # Resize the image
                self.original_unrotated = cv2.resize(self.original_unrotated, target_size, interpolation=cv2.INTER_AREA)

                # Print the new resolution
                height, width = self.original_unrotated.shape[:2]
                print(f"Resized image resolution: {width}x{height}")

                # Apply any saved rotation
                self.rotate_and_update()
                self.process_button.setEnabled(True)

    def process_image(self):
        if self.image is not None:
            # Convert to grayscale
            gray = rgb2gray(self.image)

            # Convert to binary (threshold at 0.5)
            binary = gray > 0.5

            # Invert the binary image
            inverted = invert(binary)

            # Perform skeletonization
            skeleton = skeletonize(inverted)

            # Convert boolean array to uint8 for display (multiply by 255)
            self.processed_image = (skeleton * 255).astype(np.uint8)

            # Display the skeleton
            self.skeleton_label.setBaseImage(self.processed_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSkeletonApp()
    window.show()
    sys.exit(app.exec_())
