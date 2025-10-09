import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QFileDialog,
    QSizePolicy,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)  # Set minimum size
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap:
            self.updatePixmap()

    def setNewPixmap(self, pixmap):
        self._pixmap = pixmap
        self.updatePixmap()

    def updatePixmap(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            super().setPixmap(scaled)


class MeanShiftApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mean Shift Image Processing")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize variables
        self.original_image = None
        self.processed_image = None

        self.init_ui()

    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create control panel
        control_panel = QWidget()
        control_panel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        control_panel.setFixedWidth(250)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(5)
        control_layout.setContentsMargins(5, 5, 5, 5)

        # Add load image button
        load_button = QPushButton("Load Image")
        load_button.setFixedHeight(30)
        load_button.clicked.connect(self.load_image)
        control_layout.addWidget(load_button)

        # Add process button
        self.process_button = QPushButton("Process Image")
        self.process_button.setFixedHeight(30)
        self.process_button.clicked.connect(self.process_image)
        self.process_button.setEnabled(False)
        control_layout.addWidget(self.process_button)

        # Create a widget for sliders
        sliders_widget = QWidget()
        sliders_layout = QVBoxLayout(sliders_widget)
        sliders_layout.setSpacing(5)
        sliders_layout.setContentsMargins(0, 0, 0, 0)

        # Add sliders
        self.spatial_radius_slider = self.create_slider("Spatial Radius", 5, 100, 20, sliders_layout)

        self.color_radius_slider = self.create_slider("Color Radius", 5, 100, 30, sliders_layout)

        self.scale_slider = self.create_slider("Downscale Factor", 1, 16, 1, sliders_layout)

        self.blur_slider = self.create_slider("Blur Kernel Size", 1, 31, 1, sliders_layout)

        control_layout.addWidget(sliders_widget)
        control_layout.addStretch()
        layout.addWidget(control_panel)

        # Create image layout
        image_layout = QHBoxLayout()
        image_layout.setSpacing(10)

        # Create container widgets for labels
        left_container = QWidget()
        right_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        right_layout = QVBoxLayout(right_container)

        # Create custom labels
        self.original_label = ImageLabel()
        self.processed_label = ImageLabel()

        # Add labels to layouts
        left_layout.addWidget(QLabel("Original Image"))
        left_layout.addWidget(self.original_label)
        right_layout.addWidget(QLabel("Processed Image"))
        right_layout.addWidget(self.processed_label)

        # Add containers to image layout
        image_layout.addWidget(left_container)
        image_layout.addWidget(right_container)

        # Add image layout to main layout
        image_widget = QWidget()
        image_widget.setLayout(image_layout)
        layout.addWidget(image_widget)

    def create_slider(self, name, min_val, max_val, default_val, layout):
        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setSpacing(2)
        slider_layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel(name)
        value_label = QLabel(str(default_val))
        value_label.setFixedWidth(40)
        value_label.setAlignment(Qt.AlignRight)

        header_layout.addWidget(name_label)
        header_layout.addWidget(value_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

        slider_layout.addWidget(header_widget)
        slider_layout.addWidget(slider)
        layout.addWidget(slider_container)

        return slider

    def convert_cv_to_pixmap(self, cv_img):
        height, width, channel = cv_img.shape
        bytes_per_line = channel * width
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)

    def load_image(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
            if file_name:
                self.original_image = cv2.imread(file_name)
                if self.original_image is None:
                    raise Exception("Failed to load image")

                pixmap = self.convert_cv_to_pixmap(self.original_image)
                self.original_label.setNewPixmap(pixmap)
                self.process_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading image: {str(e)}")

    def process_image(self):
        try:
            if self.original_image is None:
                raise Exception("No image loaded")

            # Get parameters from sliders
            spatial_radius = self.spatial_radius_slider.value()
            color_radius = self.color_radius_slider.value()
            scale_factor = self.scale_slider.value()
            blur_size = self.blur_slider.value()

            # Create a copy of the image
            img = self.original_image.copy()

            print("Processing image with parameters:")
            print(f"Spatial radius: {spatial_radius}")
            print(f"Color radius: {color_radius}")
            print(f"Scale factor: {scale_factor}")
            print(f"Blur size: {blur_size}")
            print(f"Original image shape: {img.shape}")

            # Downscale image
            if scale_factor > 1:
                height, width = img.shape[:2]
                new_height = height // scale_factor
                new_width = width // scale_factor
                img = cv2.resize(img, (new_width, new_height))
                print(f"Downscaled image shape: {img.shape}")

            # Apply blur if kernel size is greater than 1
            if blur_size > 1:
                blur_size = blur_size if blur_size % 2 == 1 else blur_size + 1
                img = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
                print(f"Applied blur with kernel size: {blur_size}")

            # Apply mean shift filtering
            print("Applying mean shift filtering...")
            try:
                img = cv2.pyrMeanShiftFiltering(img, spatial_radius, color_radius)
                print("Mean shift filtering completed")
            except Exception as e:
                raise Exception(f"Mean shift filtering failed: {str(e)}")

            # Resize back to original size if scaled
            if scale_factor > 1:
                img = cv2.resize(img, (self.original_image.shape[1], self.original_image.shape[0]))
                print("Resized back to original dimensions")

            self.processed_image = img

            # Convert and display the processed image
            pixmap = self.convert_cv_to_pixmap(self.processed_image)
            self.processed_label.setNewPixmap(pixmap)
            print("Image processing and display completed successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing image: {str(e)}")
            print(f"Error during processing: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeanShiftApp()
    window.show()
    sys.exit(app.exec_())
