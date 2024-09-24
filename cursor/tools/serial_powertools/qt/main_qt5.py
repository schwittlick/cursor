import sys
import logging
import random
import typing
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTextEdit, QFileDialog, QProgressBar,
                             QLabel, QLineEdit)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import serial
from serial.tools import list_ports

# Assuming these imports are available in your project structure
from cursor.collection import Collection
from cursor.device import PlotterHpglNames, MinmaxMapping
from cursor.hpgl import RESET_DEVICE, ABORT_GRAPHICS
from cursor.path import Path
from cursor.renderer.hpgl import HPGLRenderer
from cursor.tools.discovery import discover
from tools.serial_powertools.qt.serial_inspector_qt5 import SerialInspector


class SerialInspectorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inspector = SerialInspector()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Serial Inspector')
        self.setGeometry(100, 100, 1550, 900)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Inspector section
        inspector_widget = self.create_inspector_widget()
        left_layout.addWidget(inspector_widget)

        # Send File section
        send_file_widget = self.create_send_file_widget()
        left_layout.addWidget(send_file_widget)

        # Bruteforce section
        bruteforce_widget = self.create_bruteforce_widget()
        left_layout.addWidget(bruteforce_widget)

        # Plotter Info section
        plotter_info_widget = self.create_plotter_info_widget()
        left_layout.addWidget(plotter_info_widget)

        # Output section
        output_widget = self.create_output_widget()
        right_layout.addWidget(output_widget)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_inspector_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Port and Baud selection
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["1200", "9600"])
        self.baud_combo.setCurrentText("9600")
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(QLabel("Baud:"))
        port_layout.addWidget(self.baud_combo)
        layout.addLayout(port_layout)

        # Connection buttons
        conn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_serial_ports)
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.inspector.connect_serial)
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self.inspector.disconnect_serial)
        self.connection_status = QLabel("Status: Disconnected")
        conn_layout.addWidget(refresh_btn)
        conn_layout.addWidget(connect_btn)
        conn_layout.addWidget(disconnect_btn)
        conn_layout.addWidget(self.connection_status)
        layout.addLayout(conn_layout)

        # Command input
        cmd_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.send_command)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_command)
        cmd_layout.addWidget(self.command_input)
        cmd_layout.addWidget(send_btn)
        layout.addLayout(cmd_layout)

        # Command buttons
        cmd_buttons = [
            ("IN;", "IN;"), ("OA;", "OA;"), ("OE;", "OE;"), ("OH;", "OH;"), ("OI;", "OI;"),
            ("PU;", "PU;"), ("PD;", "PD;"),
            ("VS1;", "VS1;"), ("VS10;", "VS10;"), ("VS20;", "VS20;"), ("VS40;", "VS40;"), ("VS80;", "VS80;"),
            ("PA0,0;", "PA0,0;"), ("PA10000,10000;", "PA10000,10000;"),
            ("PArandom(),random();", self.generate_random_pa),
            ("ESC.R;", RESET_DEVICE + ";"), ("ESC.K;", ABORT_GRAPHICS + ";"),
            ("SP0;", "SP0;"), ("SP1;", "SP1;"), ("SP2;", "SP2;"), ("SP3;", "SP3;"), ("SP4;", "SP4;"),
            ("SP5;", "SP5;"), ("SP6;", "SP6;"), ("SP7;", "SP7;"), ("SP8;", "SP8;"),
        ]

        for i in range(0, len(cmd_buttons), 5):
            btn_layout = QHBoxLayout()
            for label, command in cmd_buttons[i:i + 5]:
                btn = QPushButton(label)
                btn.clicked.connect(lambda _, cmd=command: self.send_command(cmd))
                btn_layout.addWidget(btn)
            layout.addLayout(btn_layout)

        # Special command buttons
        special_layout = QHBoxLayout()
        special_buttons = [
            ("Random Swirl", self.generate_random_swirl),
            ("Random dot walk", self.generate_random_dot_walk),
            ("Fill square (dotted)", self.generate_filled_square_dotted),
            ("Fill square (lines)", self.generate_filled_square_lines),
        ]
        for label, func in special_buttons:
            btn = QPushButton(label)
            btn.clicked.connect(func)
            special_layout.addWidget(btn)
        layout.addLayout(special_layout)

        widget.setLayout(layout)
        return widget

    def create_send_file_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        select_file_btn = QPushButton("Select File")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)

        send_layout = QHBoxLayout()
        send_async_btn = QPushButton("Send Async")
        send_async_btn.clicked.connect(self.inspector.send_serial_file)
        stop_sending_btn = QPushButton("Stop sending")
        stop_sending_btn.clicked.connect(self.inspector.stop_send_serial_file)
        send_layout.addWidget(send_async_btn)
        send_layout.addWidget(stop_sending_btn)
        layout.addLayout(send_layout)

        self.send_file_progress = QProgressBar()
        layout.addWidget(self.send_file_progress)

        widget.setLayout(layout)
        return widget

    def create_bruteforce_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.bruteforce_progress = QProgressBar()
        layout.addWidget(self.bruteforce_progress)

        btn_layout = QHBoxLayout()
        start_bruteforce_btn = QPushButton("Bruteforce")
        start_bruteforce_btn.clicked.connect(self.inspector.start_bruteforce_progress)
        stop_bruteforce_btn = QPushButton("Stop Bruteforce")
        stop_bruteforce_btn.clicked.connect(self.inspector.stop_bruteforce_progress)
        self.timeout_combo = QComboBox()
        self.timeout_combo.addItems(["0.1", "0.3", "0.7", "1.0", "2.0"])
        self.timeout_combo.setCurrentText("1.0")
        btn_layout.addWidget(start_bruteforce_btn)
        btn_layout.addWidget(stop_bruteforce_btn)
        btn_layout.addWidget(QLabel("Timeout:"))
        btn_layout.addWidget(self.timeout_combo)
        layout.addLayout(btn_layout)

        widget.setLayout(layout)
        return widget

    def create_plotter_info_widget(self):
        widget = QWidget()
        layout = QHBoxLayout()

        get_model_btn = QPushButton("Get model")
        get_model_btn.clicked.connect(self.inspector.get_plotter_model)
        self.plotter_model_label = QLabel("Plotter Model: ")
        layout.addWidget(get_model_btn)
        layout.addWidget(self.plotter_model_label)

        widget.setLayout(layout)
        return widget

    def create_output_widget(self):
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        return self.output_text

    def refresh_serial_ports(self):
        logging.info("Starting refresh..")
        discovered_ports = discover(timeout=0.5)
        ports_with_model = [f"{port[0]} -> {port[1]}" for port in discovered_ports]
        self.port_combo.clear()
        self.port_combo.addItems(ports_with_model)

    def send_command(self, command=None):
        if command is None:
            command = self.command_input.text()
        self.inspector.send_serial_command(command)
        self.command_input.clear()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_path.setText(file_path)

    def print_output(self, text: str):
        self.output_text.append(f"{text}")

    # Generate functions (these would be implemented similarly to the original code)
    def generate_random_swirl(self):
        # Implementation similar to the original code
        pass

    def generate_random_dot_walk(self):
        # Implementation similar to the original code
        pass

    def generate_filled_square_dotted(self):
        # Implementation similar to the original code
        pass

    def generate_filled_square_lines(self):
        # Implementation similar to the original code
        pass

    def generate_random_pa(self):
        x = random.randint(0, 10000)
        y = random.randint(0, 10000)
        return f"PA{x},{y};"


def main():
    app = QApplication(sys.argv)
    gui = SerialInspectorGUI()
    gui.show()

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Redirect logging to GUI
    class QTextEditLogger(logging.Handler):
        def __init__(self, widget):
            super().__init__()
            self.widget = widget

        def emit(self, record):
            msg = self.format(record)
            self.widget.print_output(msg)

    logger = logging.getLogger()
    logger.addHandler(QTextEditLogger(gui))

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
