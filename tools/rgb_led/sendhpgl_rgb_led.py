import sys
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QFileDialog, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from time import sleep

from hpgl.hpgl_tokenize import tokenizer
from hpgl.plotter.plotter import HPGLPlotter


class PlotterThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, plotter_port, arduino_port, hpgl_data):
        super().__init__()
        self.plotter_port = plotter_port
        self.arduino_port = arduino_port
        self.hpgl_data = hpgl_data
        self.is_running = True

    def run(self):
        try:
            plotter = HPGLPlotter(serial.Serial(self.plotter_port))
            arduino = serial.Serial(self.arduino_port, baudrate=9600, timeout=1)
            commands = tokenizer(self.hpgl_data)

            for i, cmd in enumerate(commands):
                if not self.is_running:
                    break

                self.progress.emit(int((i / len(commands)) * 100))
                self.status.emit(f"Processing command: {cmd}")

                if cmd.startswith("PD"):
                    plotter.write(f"{cmd};")
                elif cmd.startswith("PU"):
                    arduino.write("RGB0,0,0;".encode('utf-8'))
                    plotter.write(f"{cmd};")
                elif cmd.startswith("PA"):
                    pos = cmd[2:].split(',')
                    po = (int(pos[0]), int(pos[1]))
                    plotter.write(f"PA{po[0]},{po[1]};")
                    self._poll_position(plotter, po)
                elif cmd.startswith("RGB"):
                    arduino.write(f"{cmd};".encode('utf-8'))
                    arduino.readline()  # Read acknowledgment
                elif cmd.startswith("VS"):
                    plotter.write(f"{cmd};")

                sleep(0.1)

            self.progress.emit(100)
            self.status.emit("Plotting completed!")
            self.finished.emit()

        except Exception as e:
            self.status.emit(f"Error: {str(e)}")
            self.finished.emit()

    def _poll_position(self, plotter, target_pos):
        attempts = 0
        while attempts < 20 and self.is_running:
            current_pos = plotter.get_position()
            if current_pos == target_pos:
                return True
            attempts += 1
            sleep(0.1)
        return False

    def stop(self):
        self.is_running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RGB LED Plotter Controller")
        self.setMinimumSize(600, 400)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Serial port selection
        port_layout = QHBoxLayout()

        # Plotter port selection
        plotter_layout = QVBoxLayout()
        plotter_layout.addWidget(QLabel("Plotter Port:"))
        self.plotter_port_combo = QComboBox()
        plotter_layout.addWidget(self.plotter_port_combo)
        port_layout.addLayout(plotter_layout)

        # Arduino port selection
        arduino_layout = QVBoxLayout()
        arduino_layout.addWidget(QLabel("Arduino Port:"))
        self.arduino_port_combo = QComboBox()
        arduino_layout.addWidget(self.arduino_port_combo)
        port_layout.addLayout(arduino_layout)

        # Refresh ports button
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_btn)

        layout.addLayout(port_layout)

        # File selection
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        file_layout.addWidget(self.file_path_label)

        load_btn = QPushButton("Load HPGL File")
        load_btn.clicked.connect(self.load_file)
        file_layout.addWidget(load_btn)

        layout.addLayout(file_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Status log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Plotting")
        self.start_btn.clicked.connect(self.start_plotting)
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_plotting)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # Initialize
        self.hpgl_data = None
        self.plotter_thread = None
        self.refresh_ports()

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]

        self.plotter_port_combo.clear()
        self.arduino_port_combo.clear()

        self.plotter_port_combo.addItems(ports)
        self.arduino_port_combo.addItems(ports)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open HPGL File", "", "HPGL Files (*.hpgl);;All Files (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.hpgl_data = ''.join(f.readlines())
                self.hpgl_data = self.hpgl_data.replace(" ", '').replace("\n", '').replace("\r", '')
                self.file_path_label.setText(file_path)
                self.start_btn.setEnabled(True)
                self.log_message(f"Loaded file: {file_path}")
            except Exception as e:
                self.log_message(f"Error loading file: {str(e)}")

    def start_plotting(self):
        if not self.hpgl_data:
            self.log_message("No HPGL file loaded!")
            return

        plotter_port = self.plotter_port_combo.currentText()
        arduino_port = self.arduino_port_combo.currentText()

        if not plotter_port or not arduino_port:
            self.log_message("Please select both plotter and Arduino ports!")
            return

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)

        self.plotter_thread = PlotterThread(plotter_port, arduino_port, self.hpgl_data)
        self.plotter_thread.progress.connect(self.update_progress)
        self.plotter_thread.status.connect(self.log_message)
        self.plotter_thread.finished.connect(self.plotting_finished)
        self.plotter_thread.start()

    def stop_plotting(self):
        if self.plotter_thread and self.plotter_thread.isRunning():
            self.plotter_thread.stop()
            self.plotter_thread.wait()
            self.log_message("Plotting stopped by user")
            self.plotting_finished()

    def plotting_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def log_message(self, message):
        self.log_text.append(message)

    def closeEvent(self, event):
        self.stop_plotting()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
