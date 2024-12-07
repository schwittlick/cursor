import sys
import cv2
import numpy as np
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox,
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                             QFileDialog)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


class ImageColorReplacer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Color Replacer")

        # Available colors (RGB format)
        self.colors = {
            'Death Black': (0, 0, 0),
            'Bogotà White': (255, 255, 255),
            'Flash Yellow': (255, 238, 0),
            'Sunray Yellow': (255, 178, 91),
            'Clockwork Orange': (254, 100, 7),
            'Ferrari Red': (207, 37, 37),
            'Piggy Pink': (236, 122, 178),
            'Jellyfish Fuchsia': (255, 34, 155),
            'Goldrake Purple': (67, 50, 154),
            'Iceberg Blue': (80, 180, 220),
            'Diving Blue': (0, 45, 176),
            'Miami Green': (71, 255, 185),
            'Obitory Green': (0, 186, 116),
            'Laser Green': (109, 195, 75),
            'Burning Chrome': (207, 207, 207),
            'Klondike Gold': (154, 119, 48),
            'Neon Orange': (255, 125, 102),
            'Neon Fuchsia': (255, 81, 181),
            'Neon Green': (0, 249, 0),
        }

        self.image = None
        self.processed_image = None
        self.initUI()

    def initUI(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create controls
        controls_layout = QHBoxLayout()

        # Black color replacement combo box
        black_label = QLabel("Replace Black with:")
        self.black_combo = QComboBox()
        self.black_combo.addItems(self.colors.keys())
        self.black_combo.currentTextChanged.connect(self.process_image)

        # White color replacement combo box
        white_label = QLabel("Replace White with:")
        self.white_combo = QComboBox()
        self.white_combo.addItems(self.colors.keys())
        self.white_combo.currentTextChanged.connect(self.process_image)

        # Add controls to layout
        controls_layout.addWidget(black_label)
        controls_layout.addWidget(self.black_combo)
        controls_layout.addWidget(white_label)
        controls_layout.addWidget(self.white_combo)

        # Buttons
        button_layout = QHBoxLayout()
        load_button = QPushButton("Load Image")
        load_button.clicked.connect(self.load_image)
        save_button = QPushButton("Save Image (S)")
        save_button.clicked.connect(self.save_image)

        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # Add all layouts to main layout
        layout.addLayout(controls_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.image_label)

        # Set window size
        self.setMinimumSize(800, 600)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.save_image()
        elif event.key() == Qt.Key_R:
            self.randomize_colors()

    def randomize_colors(self):
        color_names = list(self.colors.keys())
        black_color = random.choice(color_names)
        white_color = random.choice(color_names)

        # Ensure the colors are different
        while white_color == black_color:
            white_color = random.choice(color_names)

        self.black_combo.setCurrentText(black_color)
        self.white_combo.setCurrentText(white_color)
        self.process_image()

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            # Load image with OpenCV
            self.image = cv2.imread(file_name)
            if self.image is not None:
                # Scale image up 2x
                self.image = cv2.resize(self.image, None, fx=2, fy=2,
                                        interpolation=cv2.INTER_NEAREST_EXACT)
                self.process_image()

    def process_image(self):
        if self.image is None:
            return

        # Get selected colors
        black_color = self.colors[self.black_combo.currentText()]
        white_color = self.colors[self.white_combo.currentText()]

        # Create a copy of the image
        self.processed_image = self.image.copy()

        # Create masks for black and white pixels (with tolerance)
        black_mask = np.all(self.image < 30, axis=2)
        white_mask = np.all(self.image > 225, axis=2)

        # Replace colors
        self.processed_image[black_mask] = black_color
        self.processed_image[white_mask] = white_color

        # Rotate the image 180 degrees
        self.processed_image = cv2.rotate(self.processed_image, cv2.ROTATE_180)

        # Convert to QImage and display
        h, w, ch = self.processed_image.shape
        q_image = QImage(self.processed_image.data, w, h, w * ch, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Scale pixmap to fit label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_label.size(),
                                      Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def save_image(self):
        if self.processed_image is None:
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                   "PNG Files (*.png);;JPEG Files (*.jpg)")
        if file_name:
            bgr_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_name, bgr_image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageColorReplacer()
    window.show()
    sys.exit(app.exec_())
