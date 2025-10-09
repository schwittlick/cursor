import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QOpenGLWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSlider,
    QFileDialog,
)
from PyQt5.QtCore import QTimer, Qt
from OpenGL.GL import *
import time
import os

from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.parser import HPGLParser


class HPGLVisualizer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands = []
        self.current_command = 0
        self.pen_down = False
        self.scale = 0.025
        self.speed = 8  # Default speed (VS8)
        self.animation_speed = 1.0  # Animation speed multiplier
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_step)
        self.last_update_time = 0
        self.bb = None

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(0.3)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if not self.bb:
            # Swap dimensions for 90° rotation
            glOrtho(0, 11000, 16000, 0, -1, 1)
        else:
            # Swap dimensions for 90° rotation
            glOrtho(self.bb.y, self.bb.y2, self.bb.x2, self.bb.x, -1, 1)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINES)
        for i in range(self.current_command):
            cmd = self.commands[i]
            if cmd[0] == "PD":
                # Rotate coordinates 90° clockwise: (x,y) -> (y,-x)
                glVertex2f(cmd[1][1], cmd[1][0])
                glVertex2f(cmd[2][1], cmd[2][0])
        glEnd()

    def load_hpgl(self, filename):
        with open(filename, "r") as file:
            hpgl_data = file.read().replace("\n", "")

        coll = HPGLParser().parse(hpgl_data)
        self.bb = coll.bb()
        tokens = tokenizer(hpgl_data)

        self.commands = []
        current_pos = (0, 0)
        self.pen_down = False

        for token in tokens:
            cmd = token[:2]
            params = token[2:].split(",")

            if cmd == "PD":
                self.pen_down = True
            elif cmd == "PU":
                self.pen_down = False
            elif cmd == "PA":
                if params and len(params) >= 2:
                    new_pos = (int(params[0]), int(params[1]))
                    if self.pen_down:
                        self.commands.append(("PD", current_pos, new_pos))
                    current_pos = new_pos
            elif cmd == "VS":
                if params:
                    self.speed = int(params[0])

        print(f"Loaded {len(self.commands)} commands")
        self.current_command = 0
        self.update()

    def start_animation(self):
        self.current_command = 0
        self.last_update_time = time.time()
        self.animation_timer.start(0)  # Run as fast as possible

    def animate_step(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        commands_to_process = int(elapsed_time * self.speed * self.animation_speed * 1000)

        if commands_to_process > 0:
            self.current_command = min(self.current_command + commands_to_process, len(self.commands))
            self.update()
            self.last_update_time = current_time

        if self.current_command >= len(self.commands):
            self.animation_timer.stop()

    def change_speed(self, value):
        self.animation_speed = value / 10.0


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" ")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.visualizer = HPGLVisualizer()
        layout.addWidget(self.visualizer)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_hpgl)
        button_layout.addWidget(load_button)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_animation)
        button_layout.addWidget(start_button)

        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setMinimum(1)
        speed_slider.setMaximum(100)
        speed_slider.setValue(10)
        speed_slider.valueChanged.connect(self.change_speed)
        layout.addWidget(speed_slider)

    def load_hpgl(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open HPGL file", "", "HPGL files (*.hpgl)")
        if filename:
            self.visualizer.load_hpgl(filename)
            # Update window title to include filename
            base_filename = os.path.basename(filename)
            self.setWindowTitle(f"{base_filename}")

    def start_animation(self):
        self.visualizer.start_animation()

    def change_speed(self, value):
        self.visualizer.change_speed(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
