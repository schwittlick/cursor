import logging
import os
import random
import sys
import time

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QShortcut,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from cursor.hpgl import ABORT_GRAPHICS, RESET_DEVICE
from cursor.timer import Timer
from cursor.tools.discovery import discover
from cursor.tools.serial_powertools.qt.progress_reporter import ProgressReporter
from cursor.tools.serial_powertools.qt.serial_inspector_qt5 import SerialInspector


class ThreadSafeLogHandler(QObject, logging.Handler):
    new_log_record = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        super(logging.Handler).__init__()

    def emit(self, record):
        msg = self.format(record)
        self.new_log_record.emit(msg)


class SerialPortDiscoveryWorker(QObject):
    finished = pyqtSignal(list)

    def discover_ports(self):
        discovered_ports = discover(timeout=0.5)
        ports_with_model = [f"{port[0]} -> {port[1]}" for port in discovered_ports]
        self.finished.emit(ports_with_model)


class SerialInspectorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inspector = SerialInspector()
        self.log_handler = None
        self.init_ui()
        self.setup_logging()
        self.setup_shortcuts()

        self.inspector.connection_status_changed.connect(self.update_connection_status)
        self.inspector.file_progress_updated.connect(self.update_file_progress)

        self.send_file_timer = Timer()
        self._progress_reporter: ProgressReporter | None = None

        # Progress tracking for time estimation
        self.recent_progress_samples = []  # list of (timestamp, progress) tuples
        self.sample_window = 500

    def init_ui(self):
        self.setWindowTitle("Plotter Power Tools")
        # self.setGeometry(100, 100, 1550, 900)

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

        insert_command_widget = self.create_insert_command_widget()
        left_layout.addWidget(insert_command_widget)

        self.inspector.command_sent.connect(self.update_command_log)

        # Add a stretch factor to push all widgets to the top
        left_layout.addStretch(1)

        # Output section
        output_widget = self.create_output_widget()
        right_layout.addWidget(output_widget)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def insert_command(self):
        command = self.insert_command_input.text()
        logging.info(f"Inserting command: {command}")
        if command:
            self.inspector.insert_command(command)

    def update_command_log(self, command):
        logging.info(f"Inserted: {command}")

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.log_handler = ThreadSafeLogHandler(self)
        self.log_handler.new_log_record.connect(self.print_output)
        logging.getLogger().addHandler(self.log_handler)

    def setup_shortcuts(self):
        # Setup ESC key to close the application
        self.shortcut_close = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut_close.activated.connect(self.close)

    def closeEvent(self, event):
        # This method is called when the window is closed
        self.shutdown()
        event.accept()

    def shutdown(self):
        logging.info("Shutting down the application...")

        if self.inspector.check():
            self.inspector.disconnect_serial()

        if self.inspector.async_sender:
            self.inspector.async_sender.stop()

        logging.info("Application shutdown complete.")

        # Remove the log handler to prevent errors during Python shutdown
        if self.log_handler:
            logger = logging.getLogger()
            logger.removeHandler(self.log_handler)
            self.log_handler.close()
            self.log_handler = None

    def print_output(self, text: str):
        self.output_text.appendPlainText(text)

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
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connection_status = QLabel("Status: Disconnected")
        conn_layout.addWidget(refresh_btn)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.connection_status)
        layout.addLayout(conn_layout)

        # Command input
        cmd_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.send_command)
        send_btn = QPushButton("Send CMD")
        send_btn.clicked.connect(self.send_command)
        cmd_layout.addWidget(self.command_input)
        cmd_layout.addWidget(send_btn)
        layout.addLayout(cmd_layout)

        # Command buttons
        cmd_buttons = [
            ("IN;", "IN;"),
            ("OA;", "OA;"),
            ("OE;", "OE;"),
            ("OH;", "OH;"),
            ("OI;", "OI;"),
            ("PU;", "PU;"),
            ("PD;", "PD;"),
            ("PA0,0;", "PA0,0;"),
            ("PA10000,10000;", "PA10000,10000;"),
            ("PArandom(),random();", self.generate_random_pa()),
            ("ESC.R (reset device);", RESET_DEVICE + ";"),
            ("ESC.K; (abort graphics)", ABORT_GRAPHICS + ";"),
        ]

        vs = [
            ("VS1;", "VS1;"),
            ("VS10;", "VS10;"),
            ("VS20;", "VS20;"),
            ("VS40;", "VS40;"),
            ("VS80;", "VS80;"),
            ("VS100;", "VS100;"),
        ]

        pen_select = [
            ("SP0;", "SP0;"),
            ("SP1;", "SP1;"),
            ("SP2;", "SP2;"),
            ("SP3;", "SP3;"),
            ("SP4;", "SP4;"),
            ("SP5;", "SP5;"),
            ("SP6;", "SP6;"),
            ("SP7;", "SP7;"),
            ("SP8;", "SP8;"),
        ]

        elements_per_line = 2
        for i in range(0, len(cmd_buttons), elements_per_line):
            btn_layout = QHBoxLayout()
            for label, command in cmd_buttons[i : i + elements_per_line]:
                btn = QPushButton(label)
                btn.clicked.connect(lambda _, cmd=command: self.send_command(cmd))
                btn_layout.addWidget(btn)
            layout.addLayout(btn_layout)

        elements_per_line = 3

        for i in range(0, len(pen_select), elements_per_line):
            btn_layout = QHBoxLayout()
            for label, command in pen_select[i : i + elements_per_line]:
                btn = QPushButton(label)
                btn.clicked.connect(lambda _, cmd=command: self.send_command(cmd))
                btn_layout.addWidget(btn)
            layout.addLayout(btn_layout)

        elements_per_line = 3

        for i in range(0, len(vs), elements_per_line):
            btn_layout = QHBoxLayout()
            for label, command in vs[i : i + elements_per_line]:
                btn = QPushButton(label)
                btn.clicked.connect(lambda _, cmd=command: self.send_command(cmd))
                btn_layout.addWidget(btn)
            layout.addLayout(btn_layout)

        widget.setLayout(layout)
        return widget

    def connect_to_port(self):
        port = self.port_combo.currentText().split(" ")[0]  # Get the selected port
        baud = int(self.baud_combo.currentText())  # Get the selected baud rate
        self.inspector.connect_serial(port, baud)

    def create_send_file_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setVisible(False)  # hidden, keeps path for logic

        self.selected_file_label = QLabel("No file selected")
        layout.addWidget(self.selected_file_label)

        file_layout = QHBoxLayout()
        select_file_btn = QPushButton("Select File")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_btn)

        send_async_btn = QPushButton("Send")
        send_async_btn.clicked.connect(self.send_file)
        pause_async_btn = QPushButton("Pause")
        pause_async_btn.clicked.connect(self.pause_send_file)
        stop_sending_btn = QPushButton("Abort")
        stop_sending_btn.clicked.connect(self.stop_send_file)

        file_layout.addWidget(send_async_btn)
        file_layout.addWidget(pause_async_btn)
        file_layout.addWidget(stop_sending_btn)

        layout.addLayout(file_layout)

        slider_layout = QHBoxLayout()
        slider_label = QLabel("Batch Size:")
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(40)
        self.slider.setValue(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.batch_size_value_label = QLabel("5")
        self.slider.valueChanged.connect(self.update_batch_size)
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.batch_size_value_label)

        # Start percentage input
        percent_label = QLabel("Start %:")
        self.start_percentage_input = QLineEdit()
        self.start_percentage_input.setPlaceholderText("0")
        self.start_percentage_input.setMaximumWidth(60)
        slider_layout.addWidget(percent_label)
        slider_layout.addWidget(self.start_percentage_input)

        layout.addLayout(slider_layout)

        max_memory_slider_layout = QHBoxLayout()
        max_memory_slider_label = QLabel("Memory limit:")
        self.max_memory_slider = QSlider()
        self.max_memory_slider.setOrientation(Qt.Horizontal)
        self.max_memory_slider.setMinimum(32)
        self.max_memory_slider.setMaximum(1024)
        self.max_memory_slider.setValue(64)
        self.max_memory_slider.setTickPosition(QSlider.TicksBelow)
        self.max_memory_slider.setTickInterval(32)
        self.max_memory_slider_label = QLabel("64")
        self.max_memory_slider.valueChanged.connect(self.update_memory_limit)
        max_memory_slider_layout.addWidget(max_memory_slider_label)
        max_memory_slider_layout.addWidget(self.max_memory_slider)
        max_memory_slider_layout.addWidget(self.max_memory_slider_label)
        layout.addLayout(max_memory_slider_layout)

        progress_layout = QHBoxLayout()
        self.send_file_progress = QProgressBar()
        self.send_file_progress.setRange(0, 100)
        progress_layout.addWidget(self.send_file_progress)

        self.elapsed_label = QLabel("Elapsed: 0s")
        progress_layout.addWidget(self.elapsed_label)
        layout.addLayout(progress_layout)

        widget.setLayout(layout)
        return widget

    def create_insert_command_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        file_layout = QHBoxLayout()

        self.insert_command_input = QLineEdit()
        file_layout.addWidget(self.insert_command_input)

        self.insert_command_button = QPushButton("Insert Command")
        self.insert_command_button.clicked.connect(self.insert_command)
        file_layout.addWidget(self.insert_command_button)

        layout.addLayout(file_layout)
        widget.setLayout(layout)
        return widget

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_path_input.setText(file_path)
            self.selected_file_label.setText(os.path.basename(file_path))
            self._update_window_title()

    def send_file(self):
        file_path = self.file_path_input.text()
        if file_path:
            # Get start percentage if provided
            start_percentage = 0.0
            try:
                percentage_text = self.start_percentage_input.text().strip()
                if percentage_text:
                    start_percentage = float(percentage_text)
                    if start_percentage < 0 or start_percentage > 100:
                        logging.warning("Start percentage must be between 0 and 100. Using 0.")
                        start_percentage = 0.0
            except ValueError:
                logging.warning("Invalid start percentage value. Using 0.")
                start_percentage = 0.0

            self._progress_reporter = ProgressReporter(label=os.path.basename(file_path)).start()
            self.inspector.send_serial_file(file_path, start_percentage)
            self.send_file_timer.start()
        else:
            logging.warning("No file selected for sending.")

    def pause_send_file(self):
        self.inspector.toggle_pause()

    def stop_send_file(self):
        self.send_file_progress.setValue(0)
        self.inspector.stop_send_serial_file()

    def clear_output(self):
        self.output_text.clear()

    def create_output_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        clear_output_button = QPushButton("Clear output")
        clear_output_button.clicked.connect(self.clear_output)

        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Monospace", 8))

        layout.addWidget(self.output_text)
        layout.addWidget(clear_output_button)
        widget.setLayout(layout)
        return widget

    def refresh_serial_ports(self):
        logging.info("Starting refresh...")
        self.thread = QThread()
        self.worker = SerialPortDiscoveryWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.discover_ports)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.update_port_combo)
        self.thread.start()

    def send_command(self, command=None):
        if command is None:
            command = self.command_input.text()
        self.inspector.send_command(command)
        self.command_input.clear()

    def update_port_combo(self, ports_with_model):
        self.port_combo.clear()
        self.port_combo.addItems(ports_with_model)

    def toggle_connection(self):
        if self.inspector.check():
            self.inspector.disconnect_serial()
        else:
            port = self.port_combo.currentText().split(" ")[0]
            baud = int(self.baud_combo.currentText())
            self.inspector.connect_serial(port, baud)

    def update_connection_status(self, status):
        self.connection_status.setText(f"Status: {status}")
        if status == "Connected":
            self.connect_btn.setText("Disconnect")
        else:
            self.connect_btn.setText("Connect")
        logging.info(f"Connection status updated: {status}")
        self._update_window_title()

    def _update_window_title(self):
        parts = ["Plotter Power Tools"]
        if self.inspector.check():
            port = self.port_combo.currentText().split(" ")[0]
            baud = self.baud_combo.currentText()
            parts.append(f"{port} @ {baud}")
        file_path = self.file_path_input.text()
        if file_path:
            parts.append(os.path.basename(file_path))
        self.setWindowTitle(" - ".join(parts))

    def seconds_to_timestamp(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}min {secs}s"
        else:
            return f"{secs}s"

    def estimate_remaining_time(self, progress: float):
        """
        Estimate remaining time to reach 100% completion using a windowed moving average.
        This approach is robust to progress jumps (like skip functionality) as it only
        considers recent progress rate rather than total elapsed time.

        Args:
            progress: Float between 0 and 1 representing current progress (e.g., 0.25 = 25%)
            elapsed_seconds: Time elapsed so far in seconds (unused but kept for compatibility)

        Returns:
            Estimated remaining time in seconds, or 0.0 if estimation is not possible
        """
        current_time = time.time()
        self.recent_progress_samples.append((current_time, progress))

        # Keep only recent samples within the window
        if len(self.recent_progress_samples) > self.sample_window:
            self.recent_progress_samples.pop(0)

        # Need at least 2 samples to calculate a rate
        if len(self.recent_progress_samples) < 2:
            return 0.0

        # Calculate rate from first to last sample in window
        first_time, first_progress = self.recent_progress_samples[0]
        last_time, last_progress = self.recent_progress_samples[-1]

        time_diff = last_time - first_time
        progress_diff = last_progress - first_progress

        # Avoid division by zero and handle negative progress (shouldn't happen)
        if time_diff <= 0 or progress_diff <= 0:
            return 0.0

        # Calculate progress rate (progress per second)
        rate = progress_diff / time_diff

        # Calculate remaining progress and estimated time
        remaining_progress = 1.0 - progress

        return remaining_progress / rate

    def update_batch_size(self, value):
        self.batch_size_value_label.setText(str(value))
        if self.inspector.async_sender:
            self.inspector.async_sender.set_batchsize(value)
            logging.info(f"Batch size updated to {value}")

    def update_memory_limit(self, value) -> None:
        self.max_memory_slider_label.setText(str(value))
        if self.inspector.async_sender:
            self.inspector.async_sender.set_memory_limit(value)
            logging.info(f"Memory limit updated to {value}")

    def update_file_progress(self, idx, max_length):
        progress = int((idx / max_length) * 100)
        self.send_file_progress.setValue(progress)
        if self._progress_reporter:
            ratio = idx / max_length
            if ratio >= 1.0:
                self._progress_reporter.finish()
                self._progress_reporter = None
            else:
                self._progress_reporter.report(ratio)

        elapsed = self.send_file_timer.elapsed()

        remaining = self.estimate_remaining_time(idx / max_length)
        self.elapsed_label.setText(
            f"Elapsed: {self.seconds_to_timestamp(round(elapsed))} "
            + f"Remaining: {self.seconds_to_timestamp(round(remaining))}"
        )

    def generate_random_pa(self):
        x = random.randint(0, 10000)
        y = random.randint(0, 10000)
        return f"PA{x},{y};"


def main():
    app = QApplication(sys.argv)
    gui = SerialInspectorGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
