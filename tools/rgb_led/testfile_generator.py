import sys
import random

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from cursor import Collection, Path
from device import PlotterType, MinmaxMapping
from export import ExportWrapper
from timer import Timer


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

        self.dot_pattern_button = QPushButton("Generate random dot test pattern")
        self.dot_pattern_button.clicked.connect(self.random_dots)
        layout.addWidget(self.dot_pattern_button, alignment=Qt.AlignCenter)

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

    def add_dot_block(self, xoff, yoff, color, padding_units):
        dots = Collection()
        for y in range(5):
            for x in range(5):
                path = Path()
                path.pen_select = 1
                path.velocity = 10
                path.rgb_led_color = color
                path.add(x * padding_units + xoff, y * padding_units + yoff)
                path.add(x * padding_units + 1 + xoff, y * padding_units + 1 + yoff)
                dots.add(path)
        return dots

    def general_dot_test_pattern(self):
        dots = Collection()
        intensity = 0.5

        red = (255 * intensity, 0, 0)  # -> cyan
        dots.extend(self.add_dot_block(0, 0, red, 10))  # Red
        dots.extend(self.add_dot_block(200, 0, red, 20))  # Red
        dots.extend(self.add_dot_block(500, 0, red, 30))  # Red
        dots.extend(self.add_dot_block(900, 0, red, 40))  # Red
        dots.extend(self.add_dot_block(1400, 0, red, 50))  # Red
        dots.extend(self.add_dot_block(2000, 0, red, 50))  # Red
        dots.extend(self.add_dot_block(2700, 0, red, 60))  # Red
        dots.extend(self.add_dot_block(3400, 0, red, 70))  # Red
        dots.extend(self.add_dot_block(4200, 0, red, 80))  # Red

        green = (0, 255 * intensity, 0)  # -> magenta
        dots.extend(self.add_dot_block(0, 1000, green, 10))
        dots.extend(self.add_dot_block(200, 1000, green, 20))
        dots.extend(self.add_dot_block(500, 1000, green, 30))
        dots.extend(self.add_dot_block(900, 1000, green, 40))
        dots.extend(self.add_dot_block(1400, 1000, green, 50))
        dots.extend(self.add_dot_block(2000, 1000, green, 50))
        dots.extend(self.add_dot_block(2700, 1000, green, 60))
        dots.extend(self.add_dot_block(3400, 1000, green, 70))
        dots.extend(self.add_dot_block(4200, 1000, green, 80))

        blue = (0, 0, 255 * intensity)  # -> yellow
        dots.extend(self.add_dot_block(0, 2000, blue, 10))
        dots.extend(self.add_dot_block(200, 2000, blue, 20))
        dots.extend(self.add_dot_block(500, 2000, blue, 30))
        dots.extend(self.add_dot_block(900, 2000, blue, 40))
        dots.extend(self.add_dot_block(1400, 2000, blue, 50))
        dots.extend(self.add_dot_block(2000, 2000, blue, 50))
        dots.extend(self.add_dot_block(2700, 2000, blue, 60))
        dots.extend(self.add_dot_block(3400, 2000, blue, 70))
        dots.extend(self.add_dot_block(4200, 2000, blue, 80))

        wrapper = ExportWrapper(
            dots,
            PlotterType.ROLAND_DXY1200_A3,
            10,
            "rgb_led_plotter_testfile",
            f"dot_test_pattern_low_intensity_{Timer.timestamp()}")
        # wrapper.fit()
        wrapper.ex()

    def random_dots(self):
        dots = Collection()

        for i in range(1000):
            path = Path()
            path.pen_select = 1
            path.velocity = 10
            path.rgb_led_color = (random.uniform(0, 255), random.uniform(0, 255), random.uniform(0, 255))
            bb = MinmaxMapping.maps[PlotterType.ROLAND_DXY1200_A3]
            x, y = random.uniform(0, bb.w), random.uniform(0, bb.h)
            path.add(x, y)
            path.add(x + 1, y)
            dots.add(path)

        wrapper = ExportWrapper(
            dots,
            PlotterType.ROLAND_DXY1200_A3,
            10,
            "rgb_led_plotter_testfile",
            f"random_dots{Timer.timestamp()}",
            optimize=True)
        # wrapper.fit()
        wrapper.ex()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
