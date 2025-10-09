import logging
import pathlib
import sys
from typing import Optional

import serial
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cursor.tools.braille_converter import convert


class BrailleConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("BrailleConverter", "FileLocations")
        self.last_directory = self.settings.value("last_directory", str(pathlib.Path.home()))
        self.last_port = self.settings.value("last_port", "")

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Braille Converter")
        self.setGeometry(300, 300, 400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and add widgets
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        select_file_btn = QPushButton("Select File")
        select_file_btn.clicked.connect(self.select_file)
        layout.addWidget(select_file_btn)

        # Serial port selection
        port_label = QLabel("Select Serial Port:")
        layout.addWidget(port_label)

        self.port_combo = QComboBox()
        self.update_available_ports()
        layout.addWidget(self.port_combo)

        refresh_ports_btn = QPushButton("Refresh Ports")
        refresh_ports_btn.clicked.connect(self.update_available_ports)
        layout.addWidget(refresh_ports_btn)

        convert_btn = QPushButton("Convert and Send")
        convert_btn.clicked.connect(self.convert_and_send)
        layout.addWidget(convert_btn)

        self.selected_file: Optional[pathlib.Path] = None

    def update_available_ports(self):
        """Update the list of available serial ports"""
        self.port_combo.clear()

        # List available serial ports
        if sys.platform.startswith("win"):
            ports = ["COM%s" % (i + 1) for i in range(256)]
        else:
            ports = [f"/dev/ttyUSB{i}" for i in range(8)]
            ports.extend(f"/dev/ttyACM{i}" for i in range(8))

        available_ports = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                available_ports.append(port)
            except (OSError, serial.SerialException):
                continue

        self.port_combo.addItems(available_ports)

        # Set last used port if available
        if self.last_port in available_ports:
            self.port_combo.setCurrentText(self.last_port)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", self.last_directory, "All Files (*.*)")

        if file_path:
            self.selected_file = pathlib.Path(file_path)
            self.file_label.setText(f"Selected: {self.selected_file.name}")

            # Save the directory location
            self.last_directory = str(self.selected_file.parent)
            self.settings.setValue("last_directory", self.last_directory)

    def convert_and_send(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Please select a file first!")
            return

        if not self.port_combo.currentText():
            QMessageBox.warning(self, "Error", "Please select a serial port!")
            return

        try:
            # Convert the file
            vim_data = convert(self.selected_file)

            # Setup serial connection
            port = self.port_combo.currentText()
            self.last_port = port
            self.settings.setValue("last_port", port)

            s = serial.Serial(
                port,
                9600,
                timeout=1,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=True,
            )

            # Send data
            for line in vim_data:
                logging.info(line)
                s.write(f"{line}\n".encode())

            s.close()

            QMessageBox.information(self, "Success", f"Successfully sent data to {port}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


def main():
    logging.basicConfig(level=logging.INFO)

    app = QApplication(sys.argv)
    window = BrailleConverterGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
