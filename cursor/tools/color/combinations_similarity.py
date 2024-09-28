import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, \
    QScrollArea, QGridLayout, QColorDialog, QStyledItemDelegate
from PyQt5.QtGui import QColor, QPalette, QPixmap, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QSize

import colour

from cursor.algorithm.color.combinations import ColorDictionary
from cursor.algorithm.color.copic import Copic


class ColorComboDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return super().paint(painter, option, index)

        colors = index.data(Qt.UserRole)
        if not colors:
            return super().paint(painter, option, index)

        # Draw the background
        super().paint(painter, option, index)

        # Draw the color squares
        square_size = option.rect.height() - 4
        x = option.rect.left() + 30  # Start after the index
        y = option.rect.top() + 2
        for color in colors:
            painter.fillRect(x, y, square_size, square_size, QColor(color))
            painter.drawRect(x, y, square_size, square_size)
            x += square_size + 2

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        colors = index.data(Qt.UserRole)
        if colors:
            size.setWidth(30 + len(colors) * (option.rect.height() + 2))
        return size


class CustomColorDialog(QColorDialog):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentColorChanged.connect(self.onCurrentColorChanged)

    def onCurrentColorChanged(self, color):
        self.colorChanged.emit(color)


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
                combinations[combo].append(color)
        return combinations

    def initUI(self):
        self.setWindowTitle('Color Combination to Copic')
        self.setGeometry(100, 100, 400, 600)

        main_layout = QVBoxLayout()

        # Combination selection
        self.combo_selector = QComboBox()
        self.combo_selector.setItemDelegate(ColorComboDelegate(self.combo_selector))
        for index, colors in sorted(self.combinations.items()):
            color_hexes = [color.hex for color in colors]
            self.combo_selector.addItem(str(index), color_hexes)

        self.combo_selector.setCurrentIndex(-1)  # No selection by default
        self.combo_selector.currentIndexChanged.connect(self.on_combination_selected)

        main_layout.addWidget(QLabel('Select a combination:'))
        main_layout.addWidget(self.combo_selector)

        # Color Picker
        color_picker_layout = QHBoxLayout()
        self.color_picker_button = QPushButton('Pick a Color')
        self.color_picker_button.clicked.connect(self.open_color_picker)
        self.color_display = QLabel()
        self.color_display.setFixedSize(50, 25)
        color_picker_layout.addWidget(self.color_picker_button)
        color_picker_layout.addWidget(self.color_display)
        main_layout.addLayout(color_picker_layout)

        # Scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def on_combination_selected(self, index):
        if index >= 0:
            colors = self.combo_selector.itemData(index)
            self.display_selected_colors(colors)

    def display_selected_colors(self, colors):
        self.clear_results()
        self.results_layout.addWidget(QLabel("Selected Combination Colors:"))
        for color_hex in colors:
            color_name = self.get_color_name(color_hex)
            self.display_color_info(color_hex, color_name)

    def get_color_name(self, color_hex):
        for color in self.color_dict.colors.values():
            if color.hex == color_hex:
                return color.name
        return "Unknown"

    def display_color_info(self, color_hex, color_name):
        color = QColor(color_hex)
        copic_matches = self.find_copic_matches(color)

        # Display the original color information
        result_widget = QWidget()
        result_layout = QHBoxLayout(result_widget)

        color_display = QLabel()
        color_display.setFixedSize(50, 25)
        color_display.setStyleSheet(f"background-color: {color_hex};")
        result_layout.addWidget(color_display)

        result_layout.addWidget(QLabel(f"{color_name} ({color_hex})"))

        self.results_layout.addWidget(result_widget)

        # Display Copic matches
        self.display_color_matches(color_name, color_hex, copic_matches)

    def convert_combination(self):
        index = self.combo_selector.currentIndex()
        if index >= 0:
            colors = self.combo_selector.itemData(index)
            self.display_selected_colors(colors)

    def open_color_picker(self):
        color_dialog = CustomColorDialog(self)
        color_dialog.colorChanged.connect(self.update_color_realtime)
        color_dialog.exec_()

    def update_color_realtime(self, color):
        self.color_display.setStyleSheet(f"background-color: {color.name()};")
        self.find_similar_dissimilar_colors(color)

    def find_similar_dissimilar_colors(self, color):
        self.clear_results()

        target_rgb = (color.red() / 255, color.green() / 255, color.blue() / 255)
        target_xyz = colour.sRGB_to_XYZ(target_rgb)
        target_lab = colour.XYZ_to_Lab(target_xyz)

        copic_matches = []

        for copic_color in self.copic.available_colors.values():
            copic_xyz = colour.sRGB_to_XYZ(copic_color.as_srgb())
            copic_lab = colour.XYZ_to_Lab(copic_xyz)
            delta = colour.delta_E(target_lab, copic_lab, method='CIE 2000')
            copic_matches.append((copic_color, delta))

        copic_matches.sort(key=lambda x: x[1])

        # Display most similar colors
        self.results_layout.addWidget(QLabel("Most Similar Colors:"))
        self.display_color_matches("Selected Color", color.name(), copic_matches[:5])

        # Display least similar colors
        self.results_layout.addWidget(QLabel("Least Similar Colors:"))
        self.display_color_matches("Selected Color", color.name(), copic_matches[-5:])

    def find_copic_matches(self, color):
        target_rgb = (color.red() / 255, color.green() / 255, color.blue() / 255)
        target_xyz = colour.sRGB_to_XYZ(target_rgb)
        target_lab = colour.XYZ_to_Lab(target_xyz)

        copic_matches = []

        for copic_color in self.copic.available_colors.values():
            copic_xyz = colour.sRGB_to_XYZ(copic_color.as_srgb())
            copic_lab = colour.XYZ_to_Lab(copic_xyz)
            delta = colour.delta_E(target_lab, copic_lab, method='CIE 2000')
            copic_matches.append((copic_color, delta))

        return sorted(copic_matches, key=lambda x: x[1])[:5]

    def display_color_matches(self, color_name, color_hex, copic_matches):
        result_widget = QWidget()
        result_layout = QGridLayout(result_widget)

        # Original color display
        original_color_display = QLabel()
        original_color_display.setFixedSize(50, 25)
        original_color_display.setStyleSheet(f"background-color: {color_hex};")
        result_layout.addWidget(original_color_display, 0, 0)

        # Original color info
        result_layout.addWidget(QLabel(f"{color_name} ({color_hex})"), 0, 1)

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

    def clear_results(self):
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorCombinationApp()
    ex.show()
    sys.exit(app.exec_())
