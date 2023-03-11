"""
Example code showing how to create a button,
and the three ways to process button events.
"""
import arcade
import arcade.gui

import threading
import time


class GuiThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.running = True
        self.plotter = None
        self.func = None

    def run(self):
        print(f"Thread {self.thread_id} started")

        try:
            self.func(self.plotter)
        except Exception as e:
            print(f"gui thread crashed: {e}")

        print(f"Thread {self.thread_id} finished")

    def stop(self):
        self.running = False

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True


# Start a checker thread
class CheckerThread(threading.Thread):
    def __init__(self, threads):
        threading.Thread.__init__(self)
        self.threads = threads
        self.running = True

    def run(self):
        while True:
            if not self.running:
                print("checker thread finished")
                return

            time.sleep(1)
            dict_copy = self.threads.copy()
            for port, thread in dict_copy.items():
                if not thread.running:
                    # Pause the thread
                    thread.pause()
                elif not thread.is_alive():
                    # Remove the thread from the list if it's finished
                    del self.threads[port]
                    # self.threads.remove(thread)
                else:
                    # Resume the thread if it was paused
                    thread.resume()

    def stop(self):
        self.running = False


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UIFlatButton Example", resizable=True)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout()

    def add(self, button):
        self.v_box.add(button)

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
