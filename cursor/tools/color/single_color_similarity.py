import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QScrollArea

import colour

from algorithm.color.combinations import ColorDictionary
from algorithm.color.copic import Copic


class ColorComparisonApp(QWidget):
    def __init__(self):
        super().__init__()
        self.color_dict = ColorDictionary()
        self.copic = Copic()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Color Comparison Tool')
        self.setGeometry(100, 100, 500, 400)

        main_layout = QVBoxLayout()

        # Color selection
        self.color_combo = QComboBox()
        self.color_combo.addItems(sorted(self.color_dict.colors.keys()))
        main_layout.addWidget(QLabel('Select a color:'))
        main_layout.addWidget(self.color_combo)

        # Selected color display
        self.selected_color_label = QLabel('Selected Color')
        self.selected_color_display = QLabel()
        self.selected_color_display.setFixedSize(100, 50)
        main_layout.addWidget(self.selected_color_label)
        main_layout.addWidget(self.selected_color_display)

        # Compare button
        self.compare_button = QPushButton('Compare')
        self.compare_button.clicked.connect(self.compare_colors)
        main_layout.addWidget(self.compare_button)

        # Scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

        # Initial color display
        self.update_selected_color()
        self.color_combo.currentIndexChanged.connect(
            self.update_selected_color)

    def update_selected_color(self):
        color_name = self.color_combo.currentText()
        color = self.color_dict.get_color(color_name)
        self.selected_color_display.setStyleSheet(
            f"background-color: {color.hex};")
        self.selected_color_label.setText(
            f'Selected Color: {color_name} ({color.hex})')

    def compare_colors(self):
        color_name = self.color_combo.currentText()
        target_color = self.color_dict.get_color(color_name)
        target_rgb = tuple(v / 255 for v in target_color.rgb)
        target_xyz = colour.sRGB_to_XYZ(target_rgb)
        target_lab = colour.XYZ_to_Lab(target_xyz)

        sorted_colors = sorted(self.copic.available_colors.values(), key=lambda c: colour.delta_E(
            target_lab,
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(c.as_srgb())),
            method='CIE2000'
        ))

        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Display top 5 results
        for i, color in enumerate(sorted_colors[:5], 1):
            delta = colour.delta_E(
                target_lab,
                colour.XYZ_to_Lab(colour.sRGB_to_XYZ(color.as_srgb())),
                method='CIE2000'
            )
            result_widget = QWidget()
            result_layout = QHBoxLayout(result_widget)
            color_display = QLabel()
            color_display.setFixedSize(50, 25)
            color_display.setStyleSheet(
                f"background-color: rgb{color.as_rgb()};")
            result_layout.addWidget(color_display)
            result_layout.addWidget(
                QLabel(f"{i}. {color.name} ({color.code.name}) - Delta E: {delta:.2f}"))
            self.results_layout.addWidget(result_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorComparisonApp()
    ex.show()
    sys.exit(app.exec_())
