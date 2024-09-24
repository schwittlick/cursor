import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, \
    QScrollArea, QGridLayout
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

import colour

from cursor.algorithm.color.combinations import ColorDictionary
from cursor.algorithm.color.copic import Copic


class ColorCombinationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.color_dict = ColorDictionary()
        self.copic = Copic()
        self.combinations = self.get_combinations()
        self.initUI()

    def get_combinations(self):
        combinations = {}
        for color in self.color_dict.colors.values():
            for combo in color.combinations:
                if combo not in combinations:
                    combinations[combo] = []
                combinations[combo].append(color.name)
        return combinations

    def initUI(self):
        self.setWindowTitle('Color Combination to Copic')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Combination selection
        self.combo_selector = QComboBox()
        self.combo_selector.addItems([str(i) for i in sorted(self.combinations.keys())])
        main_layout.addWidget(QLabel('Select a combination:'))
        main_layout.addWidget(self.combo_selector)

        # Convert button
        self.convert_button = QPushButton('Convert to Copic')
        self.convert_button.clicked.connect(self.convert_combination)
        main_layout.addWidget(self.convert_button)

        # Scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def convert_combination(self):
        combo_number = int(self.combo_selector.currentText())
        colors = self.combinations[combo_number]

        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Display colors and their Copic matches
        for color_name in colors:
            color = self.color_dict.get_color(color_name)
            copic_matches = self.find_copic_matches(color)

            result_widget = QWidget()
            result_layout = QGridLayout(result_widget)

            # Original color display
            original_color_display = QLabel()
            original_color_display.setFixedSize(50, 25)
            original_color_display.setStyleSheet(f"background-color: {color.hex};")
            result_layout.addWidget(original_color_display, 0, 0)

            # Original color info
            result_layout.addWidget(QLabel(f"{color_name} ({color.hex})"), 0, 1)

            # Copic matches
            for i, (copic_color, delta) in enumerate(copic_matches, start=1):
                # Copic color display
                copic_color_display = QLabel()
                copic_color_display.setFixedSize(50, 25)
                copic_color_display.setStyleSheet(f"background-color: rgb{copic_color.as_rgb()};")
                result_layout.addWidget(copic_color_display, i, 0)

                # Copic color info
                result_layout.addWidget(QLabel(f"{copic_color.name} ({copic_color.code.name}) - Delta E: {delta:.2f}"),
                                        i, 1)

            self.results_layout.addWidget(result_widget)
            self.results_layout.addWidget(QLabel(""))  # Spacer

    def find_copic_matches(self, color):
        target_rgb = tuple(v / 255 for v in color.rgb)
        target_xyz = colour.sRGB_to_XYZ(target_rgb)
        target_lab = colour.XYZ_to_Lab(target_xyz)

        copic_matches = []

        for copic_color in self.copic.available_colors.values():
            copic_xyz = colour.sRGB_to_XYZ(copic_color.as_srgb())
            copic_lab = colour.XYZ_to_Lab(copic_xyz)
            delta = colour.delta_E(target_lab, copic_lab, method='CIE 2000')
            copic_matches.append((copic_color, delta))

        return sorted(copic_matches, key=lambda x: x[1])[:5]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorCombinationApp()
    ex.show()
    sys.exit(app.exec_())
