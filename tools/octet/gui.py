"""
Example code showing how to create a button,
and the three ways to process button events.
"""
import arcade
import arcade.gui

import threading
import time

import wasabi
from arcade.experimental.uislider import UISlider
from arcade.gui import UIOnChangeEvent

from tools.octet.data import all_paths
from tools.octet.plotter import Plotter



logger = wasabi.Printer(pretty=True, no_print=False)

class TestButton(arcade.gui.UIFlatButton):
    def __init__(self, plotter, col, **kwargs):
        super().__init__(**kwargs)
        self.plotter = plotter
        self.col = col

    def on_click(self, event: arcade.gui.UIOnClickEvent):

        if self.plotter.thread is None:
            # if not process_running[plotter.serial_port]:
            thread = GuiThread(self.plotter.serial_port)
            thread.plotter = self.plotter
            thread.speed = 40
            thread.c = self.col
            thread.func = Plotter.random_pos
            thread.start()


class GuiThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.running = True
        self.plotter = None
        self.speed = None
        self.func = None
        self.c = None

    def run(self):
        print(f"Thread for {self.plotter.type} at {self.plotter.serial_port} started")

        try:
            self.plotter.button.text = "running"
            self.func(self.plotter, self.c, self.speed)
            self.plotter.button.text = self.plotter.type
        except Exception as e:
            self.plotter.button.text = "crashed"
            logger.fail(f"gui thread crashed: {e}")
            logger.fail(e.__traceback__)

        print(f"Thread for {self.plotter.type} at {self.plotter.serial_port} finished")

    def stop(self):
        self.running = False

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True


# Start a checker thread
class CheckerThread(threading.Thread):
    def __init__(self, plotters):
        threading.Thread.__init__(self)
        self.plotters = plotters
        self.running = True

    def run(self):
        while True:
            if not self.running:
                print("checker thread finished")
                return

            time.sleep(1)
            threads = {}
            for plo in self.plotters:
                threads[plo.serial_port] = plo

            dict_copy = threads.copy()
            for port, plo in dict_copy.items():
                if not plo.thread:
                    continue
                if not plo.thread.running:
                    # Pause the thread
                    plo.thread.pause()
                elif not plo.thread.is_alive():
                    # Remove the thread from the list if it's finished
                    plo.thread = None
                    print(f"finished {plo.type}")
                    # self.threads.remove(thread)
                else:
                    # Resume the thread if it was paused
                    plo.thread.resume()

    def stop(self):
        self.running = False


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UIFlatButton Example", resizable=True)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box2 = arcade.gui.UIBoxLayout()

    def render_plotters(self, plotters):
        for plo in plotters:
            tb1 = TestButton(text=f"Plotter {plo.type}", width=200, plotter=plo, col=all_paths)
            plo.button = tb1
            self.add(tb1)

    def add(self, button):
        self.v_box.add(button)

    def add_slider(self, f):
        slider = UISlider(
            center_x=300,
            center_y=100,
            height=50,
            min_value=0,
            max_value=110,
            value=50,
            on_value_change=f,
        )

        @slider.event()
        def on_change(event: UIOnChangeEvent):
            f(slider.value)

        self.manager.add(slider)

    def finalize(self):
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()
