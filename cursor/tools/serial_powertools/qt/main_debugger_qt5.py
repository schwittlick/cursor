import sys

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class ConnectWorker(QObject):
    connected = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, port, baud, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr, read_timeout, write_timeout):
        super().__init__()
        self._port = port
        self._baud = baud
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._xonxoff = xonxoff
        self._rtscts = rtscts
        self._dsrdtr = dsrdtr
        self._read_timeout = read_timeout
        self._write_timeout = write_timeout
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def connect(self):
        if self._cancelled:
            return
        try:
            conn = serial.Serial(
                port=self._port,
                baudrate=self._baud,
                bytesize=self._bytesize,
                parity=self._parity,
                stopbits=self._stopbits,
                xonxoff=self._xonxoff,
                rtscts=self._rtscts,
                dsrdtr=self._dsrdtr,
                timeout=self._read_timeout,
                write_timeout=self._write_timeout,
            )
            if not self._cancelled:
                self.connected.emit(conn)
        except Exception as e:
            if not self._cancelled:
                self.failed.emit(str(e))


class ReaderWorker(QObject):
    data_received = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, conn: serial.Serial):
        super().__init__()
        self._conn = conn
        self._running = False

    def stop(self):
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            try:
                waiting = self._conn.in_waiting
                if waiting > 0:
                    data = self._conn.read(waiting)
                    self.data_received.emit(data.decode("ascii", errors="replace"))
                else:
                    QThread.msleep(20)
            except Exception as e:
                self.error.emit(str(e))
                break


class SerialDebugger(QMainWindow):
    def __init__(self):
        super().__init__()
        self._conn = None
        self._connect_thread = None
        self._connect_worker = None
        self._connect_timer = None
        self._reader_thread = None
        self._reader_worker = None
        self._init_ui()
        self._refresh_ports()

    def _init_ui(self):
        self.setWindowTitle("Serial Port Debugger")

        central = QWidget()
        root_layout = QHBoxLayout()

        left = QVBoxLayout()
        right = QVBoxLayout()

        left.addWidget(self._build_port_config_group())
        left.addWidget(self._build_connection_group())
        left.addWidget(self._build_commands_group())
        left.addStretch()

        right.addWidget(self._build_output_group())

        root_layout.addLayout(left, 1)
        root_layout.addLayout(right, 2)
        central.setLayout(root_layout)
        self.setCentralWidget(central)

    def _build_port_config_group(self):
        group = QGroupBox("Port Configuration")
        layout = QGridLayout()
        row = 0

        layout.addWidget(QLabel("Port:"), row, 0)
        self._port_combo = QComboBox()
        layout.addWidget(self._port_combo, row, 1)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_ports)
        layout.addWidget(refresh_btn, row, 2)
        row += 1

        layout.addWidget(QLabel("Baud Rate:"), row, 0)
        self._baud_combo = QComboBox()
        self._baud_combo.addItems(["300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self._baud_combo.setCurrentText("9600")
        layout.addWidget(self._baud_combo, row, 1)
        row += 1

        layout.addWidget(QLabel("Data Bits:"), row, 0)
        self._bytesize_combo = QComboBox()
        self._bytesize_combo.addItems(["5", "6", "7", "8"])
        self._bytesize_combo.setCurrentText("8")
        layout.addWidget(self._bytesize_combo, row, 1)
        row += 1

        layout.addWidget(QLabel("Parity:"), row, 0)
        self._parity_combo = QComboBox()
        self._parity_combo.addItems(["None (N)", "Even (E)", "Odd (O)", "Mark (M)", "Space (S)"])
        layout.addWidget(self._parity_combo, row, 1)
        row += 1

        layout.addWidget(QLabel("Stop Bits:"), row, 0)
        self._stopbits_combo = QComboBox()
        self._stopbits_combo.addItems(["1", "1.5", "2"])
        layout.addWidget(self._stopbits_combo, row, 1)
        row += 1

        layout.addWidget(QLabel("Flow Control:"), row, 0)
        self._flow_combo = QComboBox()
        self._flow_combo.addItems(["None", "XON/XOFF", "RTS/CTS", "DSR/DTR"])
        layout.addWidget(self._flow_combo, row, 1)
        row += 1

        layout.addWidget(QLabel("Read Timeout (s):"), row, 0)
        self._read_timeout_spin = QDoubleSpinBox()
        self._read_timeout_spin.setRange(0.1, 30.0)
        self._read_timeout_spin.setValue(2.0)
        self._read_timeout_spin.setSingleStep(0.5)
        layout.addWidget(self._read_timeout_spin, row, 1)
        row += 1

        layout.addWidget(QLabel("Write Timeout (s):"), row, 0)
        self._write_timeout_spin = QDoubleSpinBox()
        self._write_timeout_spin.setRange(0.1, 30.0)
        self._write_timeout_spin.setValue(2.0)
        self._write_timeout_spin.setSingleStep(0.5)
        layout.addWidget(self._write_timeout_spin, row, 1)
        row += 1

        layout.addWidget(QLabel("Connect Timeout (s):"), row, 0)
        self._connect_timeout_spin = QSpinBox()
        self._connect_timeout_spin.setRange(1, 30)
        self._connect_timeout_spin.setValue(5)
        layout.addWidget(self._connect_timeout_spin, row, 1)

        group.setLayout(layout)
        return group

    def _build_connection_group(self):
        group = QGroupBox("Connection")
        layout = QHBoxLayout()

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.clicked.connect(self._toggle_connection)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self._cancel_connect)
        self._cancel_btn.setEnabled(False)

        self._status_label = QLabel("Disconnected")
        self._status_label.setStyleSheet("color: red; font-weight: bold;")

        layout.addWidget(self._connect_btn)
        layout.addWidget(self._cancel_btn)
        layout.addWidget(self._status_label)
        layout.addStretch()

        group.setLayout(layout)
        return group

    def _build_commands_group(self):
        group = QGroupBox("Commands")
        layout = QVBoxLayout()

        quick_layout = QHBoxLayout()
        for label in ["OI;", "OH;", "OA;", "OE;"]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, cmd=label: self._send(cmd))
            quick_layout.addWidget(btn)
        layout.addLayout(quick_layout)

        cmd_layout = QHBoxLayout()
        self._cmd_input = QLineEdit()
        self._cmd_input.setPlaceholderText("Custom command (e.g. IN;)...")
        self._cmd_input.returnPressed.connect(self._send_custom)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send_custom)
        cmd_layout.addWidget(self._cmd_input)
        cmd_layout.addWidget(send_btn)
        layout.addLayout(cmd_layout)

        group.setLayout(layout)
        return group

    def _build_output_group(self):
        group = QGroupBox("Output")
        layout = QVBoxLayout()

        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont("Monospace", 10))

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._output.clear)

        layout.addWidget(self._output)
        layout.addWidget(clear_btn)
        group.setLayout(layout)
        return group

    def _refresh_ports(self):
        self._port_combo.clear()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self._port_combo.addItems(ports)
        self._log(f"Found {len(ports)} port(s): {', '.join(ports) if ports else 'none'}")

    def _log(self, msg: str):
        self._output.appendPlainText(f"[INFO] {msg}")

    def _log_rx(self, data: str):
        for line in data.splitlines():
            self._output.appendPlainText(f"[RX]   {line}")
        if data and not data.endswith("\n"):
            # flush partial line as-is
            pass

    def _log_tx(self, cmd: str):
        self._output.appendPlainText(f"[TX]   {cmd}")

    def _get_parity(self):
        return {
            "None (N)": serial.PARITY_NONE,
            "Even (E)": serial.PARITY_EVEN,
            "Odd (O)": serial.PARITY_ODD,
            "Mark (M)": serial.PARITY_MARK,
            "Space (S)": serial.PARITY_SPACE,
        }.get(self._parity_combo.currentText(), serial.PARITY_NONE)

    def _get_stopbits(self):
        return {
            "1": serial.STOPBITS_ONE,
            "1.5": serial.STOPBITS_ONE_POINT_FIVE,
            "2": serial.STOPBITS_TWO,
        }.get(self._stopbits_combo.currentText(), serial.STOPBITS_ONE)

    def _get_flow_control(self):
        return {
            "None": (False, False, False),
            "XON/XOFF": (True, False, False),
            "RTS/CTS": (False, True, False),
            "DSR/DTR": (False, False, True),
        }.get(self._flow_combo.currentText(), (False, False, False))

    def _toggle_connection(self):
        if self._conn and self._conn.is_open:
            self._disconnect()
        else:
            self._start_connect()

    def _start_connect(self):
        port = self._port_combo.currentText()
        if not port:
            self._log("No port selected.")
            return

        baud = int(self._baud_combo.currentText())
        bytesize = int(self._bytesize_combo.currentText())
        parity = self._get_parity()
        stopbits = self._get_stopbits()
        xonxoff, rtscts, dsrdtr = self._get_flow_control()
        read_timeout = self._read_timeout_spin.value()
        write_timeout = self._write_timeout_spin.value()
        connect_timeout_ms = self._connect_timeout_spin.value() * 1000

        self._connect_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._status_label.setText("Connecting...")
        self._status_label.setStyleSheet("color: orange; font-weight: bold;")
        self._log(f"Connecting to {port} @ {baud} baud (timeout {self._connect_timeout_spin.value()}s)...")

        self._connect_worker = ConnectWorker(
            port, baud, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr, read_timeout, write_timeout
        )
        self._connect_thread = QThread()
        self._connect_worker.moveToThread(self._connect_thread)
        self._connect_thread.started.connect(self._connect_worker.connect)
        self._connect_worker.connected.connect(self._on_connected)
        self._connect_worker.failed.connect(self._on_connect_failed)

        self._connect_timer = QTimer()
        self._connect_timer.setSingleShot(True)
        self._connect_timer.timeout.connect(self._on_connect_timeout)
        self._connect_timer.start(connect_timeout_ms)

        self._connect_thread.start()

    def _cancel_connect(self):
        if self._connect_worker:
            self._connect_worker.cancel()
        if self._connect_timer:
            self._connect_timer.stop()
        self._cleanup_connect_thread()
        self._status_label.setText("Cancelled")
        self._status_label.setStyleSheet("color: gray; font-weight: bold;")
        self._connect_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._log("Connection cancelled.")

    def _on_connect_timeout(self):
        if self._connect_worker:
            self._connect_worker.cancel()
        self._cleanup_connect_thread()
        self._status_label.setText("Timed out")
        self._status_label.setStyleSheet("color: red; font-weight: bold;")
        self._connect_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._log("Connection timed out.")

    def _on_connected(self, conn):
        if self._connect_timer:
            self._connect_timer.stop()
        self._conn = conn
        self._cleanup_connect_thread()
        self._status_label.setText(f"Connected: {conn.port}")
        self._status_label.setStyleSheet("color: green; font-weight: bold;")
        self._connect_btn.setText("Disconnect")
        self._connect_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._log(f"Connected: {conn.port} @ {conn.baudrate} | {conn.bytesize}{conn.parity}{conn.stopbits}")
        self._start_reader()

    def _on_connect_failed(self, error):
        if self._connect_timer:
            self._connect_timer.stop()
        self._cleanup_connect_thread()
        self._status_label.setText("Failed")
        self._status_label.setStyleSheet("color: red; font-weight: bold;")
        self._connect_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._log(f"Connection failed: {error}")

    def _cleanup_connect_thread(self):
        if self._connect_thread:
            self._connect_thread.quit()
            self._connect_thread.wait(1000)
            self._connect_thread = None
            self._connect_worker = None

    def _start_reader(self):
        self._reader_worker = ReaderWorker(self._conn)
        self._reader_thread = QThread()
        self._reader_worker.moveToThread(self._reader_thread)
        self._reader_thread.started.connect(self._reader_worker.run)
        self._reader_worker.data_received.connect(self._log_rx)
        self._reader_worker.error.connect(lambda e: self._log(f"Read error: {e}"))
        self._reader_thread.start()

    def _stop_reader(self):
        if self._reader_worker:
            self._reader_worker.stop()
        if self._reader_thread:
            self._reader_thread.quit()
            self._reader_thread.wait(1000)
            self._reader_thread = None
            self._reader_worker = None

    def _disconnect(self):
        self._stop_reader()
        if self._conn and self._conn.is_open:
            self._conn.close()
        self._conn = None
        self._status_label.setText("Disconnected")
        self._status_label.setStyleSheet("color: red; font-weight: bold;")
        self._connect_btn.setText("Connect")
        self._log("Disconnected.")

    def _send(self, cmd: str):
        if not self._conn or not self._conn.is_open:
            self._log("Not connected.")
            return
        try:
            self._conn.write(cmd.encode())
            self._log_tx(cmd)
        except Exception as e:
            self._log(f"Send error: {e}")

    def _send_custom(self):
        cmd = self._cmd_input.text().strip()
        if cmd:
            self._send(cmd)
            self._cmd_input.clear()

    def closeEvent(self, event):
        if self._connect_timer:
            self._connect_timer.stop()
        if self._connect_worker:
            self._connect_worker.cancel()
        self._cleanup_connect_thread()
        self._disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    gui = SerialDebugger()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
