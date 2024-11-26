import sys
import cv2
import json
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTabWidget, QSlider, QProgressBar, QScrollArea, QShortcut)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QKeySequence
from sklearn.cluster import (KMeans, DBSCAN, AgglomerativeClustering,
                             AffinityPropagation, SpectralClustering, Birch, MeanShift)
from sklearn.mixture import GaussianMixture
from hdbscan import HDBSCAN
from fcmeans import FCM
import skimage.segmentation as seg


class ClusteringWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)

    def __init__(self, algorithm, image, params):
        super().__init__()
        self.algorithm = algorithm
        self.image = image.copy()  # Make a copy to prevent reference issues
        self.params = params

    def run(self):
        try:
            print(f"Starting clustering with {self.algorithm}")
            h, w = self.image.shape[:2]
            pixels = self.image.reshape(-1, 3)

            # Normalize pixel values
            pixels = pixels.astype(float) / 255.0

            self.progress.emit(10)

            if self.algorithm == "meanshift":
                # Use scikit-learn's MeanShift instead of custom implementation
                bandwidth = self.params.get('bandwidth', 0.2)
                ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
                labels = ms.fit_predict(pixels)
                result = self.labels_to_image(labels, h, w)
            elif self.algorithm == "fuzzy_cmeans":
                # Special handling for Fuzzy C-Means
                n_clusters = int(self.params.get('n_clusters', 8))
                fcm = FCM(n_clusters=n_clusters)

                # Fit the model
                fcm.fit(pixels)

                # Get the cluster labels (using the highest membership value)
                labels = np.argmax(fcm.u, axis=1)

                # Convert labels to image
                result = self.labels_to_image(labels, h, w)

                # Alternative: use membership values for smooth transitions
                # memberships = fcm.u
                # centers = fcm.centers
                # result = np.dot(memberships, centers).reshape(h, w, 3)
            else:
                # Initialize the selected clustering algorithm
                clusterer = self.get_clusterer()
                print(f"Initialized clusterer: {clusterer}")

                self.progress.emit(30)

                # Fit and predict
                labels = clusterer.fit_predict(pixels)

                print(f"Clustering completed, labels shape: {labels.shape}")
                self.progress.emit(60)

                # Convert labels to image
                result = self.labels_to_image(labels, h, w)

            self.progress.emit(100)
            print("Emitting finished signal")
            self.finished.emit(result)

        except Exception as e:
            print(f"Error in clustering: {str(e)}")
            self.error.emit(str(e))
            self.progress.emit(0)

    def get_clusterer(self):
        if self.algorithm == "kmeans":
            return KMeans(n_clusters=int(self.params.get('n_clusters', 8)))
        elif self.algorithm == "dbscan":
            return DBSCAN(eps=self.params.get('eps', 0.3),
                          min_samples=int(self.params.get('min_samples', 5)))
        elif self.algorithm == "gmm":
            return GaussianMixture(n_components=int(self.params.get('n_components', 8)))
        elif self.algorithm == "hierarchical":
            return AgglomerativeClustering(n_clusters=int(self.params.get('n_clusters', 8)))
        elif self.algorithm == "affinity":
            return AffinityPropagation(damping=self.params.get('damping', 0.5))
        elif self.algorithm == "spectral":
            return SpectralClustering(n_clusters=int(self.params.get('n_clusters', 8)))
        elif self.algorithm == "birch":
            return Birch(n_clusters=int(self.params.get('n_clusters', 8)))
        elif self.algorithm == "hdbscan":
            return HDBSCAN(min_cluster_size=int(self.params.get('min_cluster_size', 5)))
        elif self.algorithm == "fuzzy_cmeans":
            return FCM(n_clusters=int(self.params.get('n_clusters', 8)))

    def labels_to_image(self, labels, height, width):
        # Create color map for unique labels
        unique_labels = np.unique(labels)
        colors = np.random.rand(len(unique_labels), 3)

        # Map labels to colors
        result = colors[labels]
        return result.reshape(height, width, 3)


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._update_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_pixmap()

    def _update_pixmap(self):
        if self._pixmap:
            scaled_pixmap = self._pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.FastTransformation
            )
            super().setPixmap(scaled_pixmap)


class AlgorithmTab(QWidget):
    def __init__(self, algorithm_name, params, parent=None):
        super().__init__(parent)
        self.algorithm_name = algorithm_name
        self.params = params
        self.sliders = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Parameters section
        params_widget = QWidget()
        params_layout = QVBoxLayout()
        params_widget.setLayout(params_layout)

        for param_name, param_info in self.params.items():
            slider_layout = QHBoxLayout()
            label = QLabel(f"{param_name}: {param_info['default']:.2f}")

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(int(param_info['min'] * 100))
            slider.setMaximum(int(param_info['max'] * 100))
            slider.setValue(int(param_info['default'] * 100))
            slider.valueChanged.connect(
                lambda value, label=label, name=param_name:
                label.setText(f"{name}: {value / 100:.2f}"))

            self.sliders[param_name] = slider
            slider_layout.addWidget(label)
            slider_layout.addWidget(slider)
            params_layout.addLayout(slider_layout)

        layout.addWidget(params_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Result image label with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.result_label = ImageLabel()
        scroll_area.setWidget(self.result_label)
        layout.addWidget(scroll_area)

        # Apply button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_clustering)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def get_params(self):
        return {name: slider.value() / 100
                for name, slider in self.sliders.items()}

    def apply_clustering(self):
        main_window = self.window()
        if hasattr(main_window, 'current_image'):
            print(f"Applying {self.algorithm_name} clustering")
            params = self.get_params()

            # Get the processed image (scaled and blurred)
            processed_image = main_window.get_processed_image(main_window.current_image)

            self.worker = ClusteringWorker(
                self.algorithm_name,
                processed_image,
                params
            )
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.update_result)
            self.worker.error.connect(lambda msg: print(f"Error: {msg}"))
            self.worker.start()

    def update_result(self, result_image):
        print("Updating result image")
        result_image = (result_image * 255).astype(np.uint8)
        height, width = result_image.shape[:2]
        bytes_per_line = 3 * width

        q_img = QImage(result_image.data, width, height,
                       bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.result_label.setPixmap(pixmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.last_directory = self.load_last_directory()
        self.last_save_directory = self.load_last_save_directory()  # Add this line

        self.init_ui()

    def init_ui(self):
        # Enable drop events for the window
        self.setAcceptDrops(True)

        self.setWindowTitle('Image Clustering Tool')
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # Image loading section
        load_layout = QHBoxLayout()
        self.load_button = QPushButton('Load Image')
        self.load_button.clicked.connect(self.load_image)
        load_layout.addWidget(self.load_button)

        # Add drop zone label
        self.drop_label = QLabel('or drag and drop an image here')
        self.drop_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
            }
        """)
        load_layout.addWidget(self.drop_label)

        # Image processing controls
        self.scale_label = QLabel('Scale: 100%')
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(1)
        self.scale_slider.setMaximum(100)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(
            lambda value: (self.scale_label.setText(f'Scale: {value}%'),
                           self.update_display_image()))
        load_layout.addWidget(self.scale_label)
        load_layout.addWidget(self.scale_slider)

        # Add blur control
        self.blur_label = QLabel('Blur: 0')
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setMinimum(0)
        self.blur_slider.setMaximum(7)  # Max kernel size will be (2*7 + 1) = 15
        self.blur_slider.setValue(0)
        self.blur_slider.valueChanged.connect(
            lambda value: (self.blur_label.setText(f'Blur: {value}'),
                           self.update_display_image()))
        load_layout.addWidget(self.blur_label)
        load_layout.addWidget(self.blur_slider)

        layout.addLayout(load_layout)

        # Original image label with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.image_label = ImageLabel()
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)

        # Tabs for different algorithms
        self.tabs = QTabWidget()

        # Algorithm parameters
        algorithms = {
            'meanshift': {'bandwidth': {'min': 0.1, 'max': 1.0, 'default': 0.2}},
            'kmeans': {'n_clusters': {'min': 2, 'max': 20, 'default': 8}},
            'dbscan': {
                'eps': {'min': 0.1, 'max': 1.0, 'default': 0.3},
                'min_samples': {'min': 2, 'max': 20, 'default': 5}
            },
            'gmm': {'n_components': {'min': 2, 'max': 20, 'default': 8}},
            'hierarchical': {'n_clusters': {'min': 2, 'max': 20, 'default': 8}},
            'affinity': {'damping': {'min': 0.5, 'max': 1.0, 'default': 0.5}},
            'spectral': {'n_clusters': {'min': 2, 'max': 20, 'default': 8}},
            'birch': {'n_clusters': {'min': 2, 'max': 20, 'default': 8}},
            'hdbscan': {'min_cluster_size': {'min': 2, 'max': 100, 'default': 5}},
            'fuzzy_cmeans': {'n_clusters': {'min': 2, 'max': 20, 'default': 8}}
        }

        # Create tabs for each algorithm
        for algo_name, params in algorithms.items():
            tab = AlgorithmTab(algo_name, params, self)
            self.tabs.addTab(tab, algo_name.title())

        layout.addWidget(self.tabs)
        main_widget.setLayout(layout)

        self.setup_shortcuts()

    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        # Check if the dragged data contains URLs (files)
        if event.mimeData().hasUrls():
            # Get the first URL
            url = event.mimeData().urls()[0].toLocalFile()
            # Check if it's an image file
            if url.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.xpm')):
                event.acceptProposedAction()
                self.drop_label.setStyleSheet("""
                    QLabel {
                        color: #2196F3;
                        font-style: italic;
                        padding: 5px;
                        font-weight: bold;
                    }
                """)

    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        # Reset drop zone styling
        self.drop_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
            }
        """)

    def dropEvent(self, event):
        """Handle drop events"""
        # Reset drop zone styling
        self.drop_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
            }
        """)

        # Get the dropped file path
        file_path = event.mimeData().urls()[0].toLocalFile()

        # Load the image
        if file_path:
            print(f"Loading dropped image: {file_path}")
            image = cv2.imread(file_path)
            if image is None:
                print(f"Failed to load image: {file_path}")
                return

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.current_image = image
            self.update_display_image()

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

    def load_last_save_directory(self):
        try:
            config_file = os.path.join(os.path.expanduser('~'), '.watershed_gui_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('last_save_directory', '')
        except Exception as e:
            print(f"Error loading config: {e}")
        return ''

    def save_last_directory(self, directory):
        try:
            config_file = os.path.join(os.path.expanduser('~'), '.watershed_gui_config.json')
            config = {'last_directory': directory}
            if hasattr(self, 'last_save_directory'):
                config['last_save_directory'] = self.last_save_directory
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def save_last_save_directory(self, directory):
        try:
            config_file = os.path.join(os.path.expanduser('~'), '.watershed_gui_config.json')
            config = {'last_save_directory': directory}
            if hasattr(self, 'last_directory'):
                config['last_directory'] = self.last_directory
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_shortcuts(self):
        self.shortcut_apply = QShortcut(QKeySequence('A'), self)
        self.shortcut_apply.activated.connect(self.trigger_apply)

        # Add save shortcut
        self.shortcut_save = QShortcut(QKeySequence('S'), self)
        self.shortcut_save.activated.connect(self.save_processed_image)

    def trigger_apply(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, AlgorithmTab):
            current_tab.apply_clustering()

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", self.last_directory,
            "Images (*.png *.xpm *.jpg *.bmp)")

        if file_name:
            self.last_directory = os.path.dirname(file_name)
            self.save_last_directory(self.last_directory)

            print(f"Loading image: {file_name}")
            image = cv2.imread(file_name)
            if image is None:
                print(f"Failed to load image: {file_name}")
                return

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.current_image = image
            self.update_display_image()

            # Update the window title with the loaded file name
            self.setWindowTitle(f'{file_name}')

    def get_processed_image(self, image):
        """Apply scale and blur processing to the image"""
        # First scale the image
        scale = self.scale_slider.value() / 100
        height, width = image.shape[:2]
        new_size = (int(width * scale), int(height * scale))
        processed_image = cv2.resize(image, new_size)

        # Then apply blur if needed
        blur_value = self.blur_slider.value()
        if blur_value > 0:
            # Create odd-numbered kernel size
            kernel_size = (2 * blur_value + 1, 2 * blur_value + 1)
            processed_image = cv2.GaussianBlur(processed_image, kernel_size, 0)

        return processed_image

    def save_processed_image(self):
        if not hasattr(self, 'current_image'):
            print("No image to save")
            return

        # Get the processed image
        processed_image = self.get_processed_image(self.current_image)

        # Open save file dialog
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            self.last_save_directory,
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_name:
            # Update and save the last save directory
            self.last_save_directory = os.path.dirname(file_name)
            self.save_last_save_directory(self.last_save_directory)

            # Convert RGB to BGR for OpenCV
            save_image = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)

            # Get the file extension
            _, ext = os.path.splitext(file_name)
            if not ext:  # If no extension provided, default to PNG
                file_name += '.png'
                ext = '.png'

            # Save the image
            try:
                # For PNG images, we can use compression
                if ext.lower() == '.png':
                    cv2.imwrite(file_name, save_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                else:
                    cv2.imwrite(file_name, save_image)
                print(f"Image saved successfully to: {file_name}")
            except Exception as e:
                print(f"Error saving image: {e}")

    def update_display_image(self):
        if hasattr(self, 'current_image'):
            processed_image = self.get_processed_image(self.current_image)

            # Convert to QPixmap and display
            height, width = processed_image.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(processed_image.data, width, height,
                           bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_img))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
