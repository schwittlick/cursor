import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QFileDialog)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QPoint

from cursor import Collection, Path
from device import PlotterType
from export import ExportWrapper
from timer import Timer


class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []
        self.image = None
        self.drawing_image = None

    def load_image(self, filename):
        self.image = QPixmap(filename)
        self.resize(self.image.width(), self.image.height())
        self.drawing_image = QImage(self.image.width(), self.image.height(), QImage.Format_ARGB32)
        self.drawing_image.fill(Qt.transparent)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Add new point
            self.points.append(event.pos())
            # Redraw
            self.update_drawing()

    def update_drawing(self):
        if not self.drawing_image:
            return

        self.drawing_image.fill(Qt.transparent)
        painter = QPainter(self.drawing_image)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

        # Draw vertices
        for point in self.points:
            painter.drawEllipse(point, 3, 3)

        # Draw lines connecting vertices
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                painter.drawLine(self.points[i], self.points[i + 1])

            # Connect last point to first point if there are at least 3 points
            if len(self.points) >= 3:
                painter.drawLine(self.points[-1], self.points[0])

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.image:
            painter.drawPixmap(0, 0, self.image)
            painter.drawImage(0, 0, self.drawing_image)

    def save_coordinates(self, filename):
        # Convert QPoint objects to (x, y) tuples
        coordinates = [(point.x(), point.y()) for point in self.points]
        with open(filename, 'w') as f:
            json.dump(coordinates, f)

        coll = Collection()
        pa = Path()
        for point in self.points:
            pa.add(point.x(), point.y())
        coll.add(pa)

        fname = f"outline_{Timer.timestamp()}"

        wrapper = ExportWrapper(
            coll,
            PlotterType.DIY_PLOTTER_60x60,
            10,  # 25mm - 11mm
            "datasets",
            fname,
            keep_aspect_ratio=True)
        wrapper.fit()
        wrapper.ex()

    def load_coordinates(self, filename):
        with open(filename, 'r') as f:
            coordinates = json.load(f)
        self.points = [QPoint(x, y) for x, y in coordinates]
        self.update_drawing()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vertex-Based Outline Tool")

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create buttons
        load_image_button = QPushButton("Load Image")
        save_coords_button = QPushButton("Save Coordinates")
        load_coords_button = QPushButton("Load Coordinates")
        clear_button = QPushButton("Clear Outline")
        undo_button = QPushButton("Undo Last Point")

        # Create drawing widget
        self.drawing_widget = DrawingWidget()

        # Add widgets to layout
        layout.addWidget(load_image_button)
        layout.addWidget(save_coords_button)
        layout.addWidget(load_coords_button)
        layout.addWidget(clear_button)
        layout.addWidget(undo_button)
        layout.addWidget(self.drawing_widget)

        # Connect buttons to functions
        load_image_button.clicked.connect(self.load_image)
        save_coords_button.clicked.connect(self.save_coordinates)
        load_coords_button.clicked.connect(self.load_coordinates)
        clear_button.clicked.connect(self.clear_outline)
        undo_button.clicked.connect(self.undo_last_point)

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                  "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.drawing_widget.load_image(filename)
            self.resize(self.drawing_widget.size())

    def save_coordinates(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Coordinates", "",
                                                  "JSON Files (*.json)")
        if filename:
            self.drawing_widget.save_coordinates(filename)

    def load_coordinates(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Coordinates", "",
                                                  "JSON Files (*.json)")
        if filename:
            self.drawing_widget.load_coordinates(filename)

    def clear_outline(self):
        if self.drawing_widget.drawing_image:
            self.drawing_widget.points = []
            self.drawing_widget.drawing_image.fill(Qt.transparent)
            self.drawing_widget.update()

    def undo_last_point(self):
        if self.drawing_widget.points:
            self.drawing_widget.points.pop()
            self.drawing_widget.update_drawing()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
