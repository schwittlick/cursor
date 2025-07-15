import sys
import cv2
import numpy as np
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
                             QSlider, QComboBox, QGroupBox, QMessageBox,
                             QProgressDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from scipy import ndimage as ndi
from skimage import filters, color, feature
from skimage.segmentation import watershed


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 200)
        self.original_pixmap = None

    def setScaledPixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.resizeEvent(None)

    def resizeEvent(self, event):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)


class WatershedGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_directory = self.load_last_directory()
        self.initUI()
        self.image = None
        self.processed_image = None
        self.scale_factor = 1.0

        # Install event filter for keyboard events
        self.installEventFilter(self)

    def initUI(self):
        self.setWindowTitle('Watershed Segmentation Tool')
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create control panel
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(300)

        # Load image button
        load_btn = QPushButton('Load Image', self)
        load_btn.clicked.connect(self.load_image)
        control_layout.addWidget(load_btn)

        # Parameters group
        params_group = QGroupBox('Parameters')
        params_layout = QVBoxLayout()

        # Image scale slider
        self.scale_slider = self.create_slider(10, 100, 100, 'Image Scale (%):')
        params_layout.addWidget(QLabel('Image Scale:'))
        params_layout.addWidget(self.scale_slider)
        self.scale_label = QLabel('Scale: 100%')
        params_layout.addWidget(self.scale_label)

        # Gradient method selector
        self.gradient_method = QComboBox()
        self.gradient_method.addItems(['sobel', 'scharr', 'prewitt', 'roberts'])
        params_layout.addWidget(QLabel('Gradient Method:'))
        params_layout.addWidget(self.gradient_method)

        # Min distance slider
        self.min_distance = self.create_slider(1, 100, 20, 'Min Distance:')
        params_layout.addWidget(QLabel('Min Distance:'))
        params_layout.addWidget(self.min_distance)
        self.min_distance_label = QLabel('Value: 20')
        params_layout.addWidget(self.min_distance_label)

        # Min gradient slider
        self.min_gradient = self.create_slider(1, 50, 10, 'Min Gradient:')
        params_layout.addWidget(QLabel('Min Gradient:'))
        params_layout.addWidget(self.min_gradient)
        self.min_gradient_label = QLabel('Value: 10')
        params_layout.addWidget(self.min_gradient_label)

        # Compactness slider
        self.compactness = self.create_slider(0, 10, 0, 'Compactness:')
        params_layout.addWidget(QLabel('Compactness:'))
        params_layout.addWidget(self.compactness)
        self.compactness_label = QLabel('Value: 0.00')
        params_layout.addWidget(self.compactness_label)

        self.blur_slider = self.create_slider(0, 300, 0, 'Blur:')
        params_layout.addWidget(QLabel('Blur:'))
        params_layout.addWidget(self.blur_slider)
        self.blur_label = QLabel('Blur: 0')
        params_layout.addWidget(self.blur_label)

        # Connect blur slider
        self.blur_slider.valueChanged.connect(self.update_blur)
        self.blur_slider.valueChanged.connect(
            lambda v: self.blur_label.setText(f'Blur: {v}'))

        # Process button
        self.process_btn = QPushButton('Process Image', self)
        self.process_btn.clicked.connect(self.update_segmentation)
        self.process_btn.setEnabled(False)
        params_layout.addWidget(self.process_btn)

        params_group.setLayout(params_layout)
        control_layout.addWidget(params_group)

        # Add control panel to main layout
        layout.addWidget(control_panel)

        # Create image display area
        display_layout = QHBoxLayout()

        # Original image
        self.original_label = ImageLabel()
        display_layout.addWidget(self.original_label)

        # Processed image
        self.processed_label = ImageLabel()
        display_layout.addWidget(self.processed_label)

        # Add display area to main layout
        display_widget = QWidget()
        display_widget.setLayout(display_layout)
        layout.addWidget(display_widget)

        # Connect slider value changes to label updates
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_label.setText(f'Scale: {v}%'))
        self.min_distance.valueChanged.connect(
            lambda v: self.min_distance_label.setText(f'Value: {v}'))
        self.min_gradient.valueChanged.connect(
            lambda v: self.min_gradient_label.setText(f'Value: {v}'))
        self.compactness.valueChanged.connect(
            lambda v: self.compactness_label.setText(f'Value: {v / 1000:.2f}'))

    def create_slider(self, min_val, max_val, default_val, name):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval((max_val - min_val) // 10)
        return slider

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            # ESC key
            if event.key() == Qt.Key_Escape:
                self.close()
                return True
            # 'W' key
            elif event.key() == Qt.Key_W and self.process_btn.isEnabled():
                self.update_segmentation()
                return True
        return super().eventFilter(obj, event)

    def update_blur(self):
        if self.image is None:
            return

        # Store original image if not already stored
        if not hasattr(self, 'original_image'):
            self.original_image = self.image.copy()

        # Get blur value (must be odd)
        blur_value = self.blur_slider.value() * 2 + 1

        if blur_value <= 1:
            # Show original image
            self.image = self.original_image.copy()
        else:
            # Apply blur
            self.image = cv2.GaussianBlur(self.original_image, (blur_value, blur_value), 0)

        # Update display
        self.display_image(self.image, self.original_label)

    def load_last_directory(self):
        try:
            config_file = os.path.join(os.path.expanduser('~'), '.watershed_gui_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('last_directory', '')
        except Exception as e:
            print(f"Error loading config: {e}")
        return ''

    def save_last_directory(self, directory):
        try:
            config_file = os.path.join(os.path.expanduser('~'), '.watershed_gui_config.json')
            config = {'last_directory': directory}
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    # [Previous ImageLabel class remains the same...]

    def load_image(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Open Image File",
                self.last_directory,
                "Images (*.png *.xpm *.jpg *.bmp)"
            )

            if file_name:
                # Save the directory
                self.last_directory = os.path.dirname(file_name)
                self.save_last_directory(self.last_directory)

                # Read image
                self.image = cv2.imread(file_name)
                if self.image is None:
                    raise Exception("Failed to load image")

                # Convert to RGB
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

                # Store original image
                self.original_image = self.image.copy()

                # Display original image
                self.display_image(self.image, self.original_label)

                # Enable process button
                self.process_btn.setEnabled(True)

                # Reset blur slider
                self.blur_slider.setValue(0)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load image: {str(e)}"
            )

    def create_progress_dialog(self, max_value):
        progress = QProgressDialog("Processing image...", "Cancel", 0, max_value, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Processing")
        progress.setAutoClose(True)
        progress.setMinimumDuration(0)  # Show immediately
        return progress

    def update_segmentation(self):
        if self.image is None:
            return

        try:
            # Create progress dialog
            progress = self.create_progress_dialog(6)  # 6 steps total
            progress.show()
            QApplication.processEvents()

            # Step 1: Scale image
            progress.setLabelText("Scaling image...")
            scale = self.scale_slider.value() / 100.0
            if scale != 1.0:
                h, w = self.image.shape[:2]  # Use self.image which may be blurred
                new_h, new_w = int(h * scale), int(w * scale)
                scaled_image = cv2.resize(self.image, (new_w, new_h))
            else:
                scaled_image = self.image  # Use self.image which may be blurred
            progress.setValue(1)

            if progress.wasCanceled():
                return

            # Step 2: Convert to grayscale
            progress.setLabelText("Converting to grayscale...")
            if scaled_image.ndim == 3:
                gray = color.rgb2gray(scaled_image.astype(float) / 255.0)
            else:
                gray = scaled_image.astype(float) / 255.0
            progress.setValue(2)

            if progress.wasCanceled():
                return

            # Step 3: Compute gradient
            progress.setLabelText("Computing gradient...")
            gradient_method = self.gradient_method.currentText()
            if gradient_method == 'sobel':
                gradient = filters.sobel(gray)
            elif gradient_method == 'scharr':
                gradient = filters.scharr(gray)
            elif gradient_method == 'prewitt':
                gradient = filters.prewitt(gray)
            else:  # roberts
                gradient = filters.roberts(gray)
            progress.setValue(3)

            if progress.wasCanceled():
                return

            # Step 4: Find markers
            progress.setLabelText("Finding markers...")
            coordinates = feature.peak_local_max(
                gradient,
                min_distance=self.min_distance.value(),
                threshold_abs=self.min_gradient.value() / 100.0
            )
            marker_image = np.zeros_like(gradient, dtype=bool)
            marker_image[tuple(coordinates.T)] = True
            markers = ndi.label(marker_image)[0]
            progress.setValue(4)

            if progress.wasCanceled():
                return

            # Step 5: Apply watershed
            progress.setLabelText("Applying watershed...")
            segments = watershed(
                -gradient,
                markers,
                compactness=self.compactness.value() / 1000.0
            )
            progress.setValue(5)

            if progress.wasCanceled():
                return

            # Step 6: Visualize and display
            progress.setLabelText("Visualizing results...")
            colored_segments = self.visualize_segments(scaled_image, segments)

            # Scale back if needed
            if scale != 1.0:
                h, w = self.image.shape[:2]
                colored_segments = cv2.resize(colored_segments, (w, h))

            self.display_image(colored_segments, self.processed_label)
            progress.setValue(6)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Warning",
                f"Error processing image: {str(e)}"
            )

    def parametrized_watershed(self, image, gradient_method='sobel', min_distance=20,
                               min_gradient=10, compactness=0.0):
        # Convert image to float and ensure it's in range [0, 1]
        if image.ndim == 3:
            gray = color.rgb2gray(image.astype(float) / 255.0)
        else:
            gray = image.astype(float) / 255.0

        # Compute gradient
        if gradient_method == 'sobel':
            gradient = filters.sobel(gray)
        elif gradient_method == 'scharr':
            gradient = filters.scharr(gray)
        elif gradient_method == 'prewitt':
            gradient = filters.prewitt(gray)
        else:  # roberts
            gradient = filters.roberts(gray)

        # Find local maxima
        coordinates = feature.peak_local_max(
            gradient,
            min_distance=min_distance,
            threshold_abs=min_gradient / 100.0  # Normalize threshold
        )

        # Create marker image
        marker_image = np.zeros_like(gradient, dtype=bool)
        marker_image[tuple(coordinates.T)] = True

        # Generate markers
        markers = ndi.label(marker_image)[0]

        # Apply watershed
        segments = watershed(
            -gradient,
            markers,
            compactness=compactness
        )

        return segments, markers, gradient

    def visualize_segments(self, image, segments):
        try:
            unique_labels = np.unique(segments)
            random_colors = np.random.rand(len(unique_labels), 3)
            colored_segments = np.zeros_like(image, dtype=np.float64)

            for i, label in enumerate(unique_labels):
                mask = segments == label
                colored_segments[mask] = random_colors[i]

            return (colored_segments * 255).astype(np.uint8)
        except Exception as e:
            print(f"Error in visualize_segments: {str(e)}")
            raise

    def display_image(self, image, label):
        try:
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            qImg = QImage(image.data, width, height, bytesPerLine,
                          QImage.Format_RGB888).copy()
            label.setScaledPixmap(QPixmap.fromImage(qImg))

        except Exception as e:
            print(f"Error in display_image: {str(e)}")
            raise


def main():
    try:
        app = QApplication(sys.argv)
        ex = WatershedGUI()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
