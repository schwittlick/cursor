import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from cursor import Collection, Path
from device import PlotterType
from export import ExportWrapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RGB LED Plotter Testfile Generator")
        self.setMinimumSize(600, 400)

        # Create a central widget and a layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create the button
        self.generate_button = QPushButton("Generate Parallel Lines")
        self.generate_button.clicked.connect(self.generate_parallel_lines)
        layout.addWidget(self.generate_button, alignment=Qt.AlignCenter)

    def create_lines(self, color: tuple[int, int, int], offset_x: float, offset_y: float) -> Collection:
        pc = Collection()
        # Generate 10 parallel lines
        vss = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50]
        for i in range(10):
            p = Path()
            p.add(offset_x, offset_y + i * 0.1)  # Start point
            p.add(offset_x + 0.3, offset_y + i * 0.1)  # End point

            p.pen_select = 1
            p.velocity = vss[i]
            p.rgb_led_color = color
            pc.add(p)

        return pc

    def generate_parallel_lines(self):
        # Define grid layout
        grid_width = 3
        grid_height = 2
        spacing_x = 0.5
        spacing_y = 0.5

        all_lines = Collection()

        colors = [
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 255, 0)  # Yellow
        ]

        for i, color in enumerate(colors):
            row = i // grid_width
            col = i % grid_width
            offset_x = col * (0.3 + spacing_x)
            offset_y = row * (1 + spacing_y)
            lines = self.create_lines(color, offset_x, offset_y)
            all_lines.extend(lines)

        wrappe = ExportWrapper(
            all_lines,
            PlotterType.ROLAND_DXY1200_A3,
            25,
            "rgb_led_plotter_testfile",
            "parallel_lines")
        wrappe.fit()
        wrappe.ex()

        print("Parallel lines generated and exported.")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
