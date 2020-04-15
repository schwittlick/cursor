from cursor.device import DrawingMachine

import wasabi
import pathlib
import threading
import time

import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

kivy.require("2.0.0")

log = wasabi.Printer()

# p = pathlib.Path(__file__).resolve().parent.joinpath("kivy_gui.kv")
#   Builder.load_file(p.as_posix())


class MyGrid(GridLayout):

    selected_file = None

    def init_connect_area(self):
        self.machine = DrawingMachine()
        self.cols = 1
        self.connect_area = GridLayout()
        self.connect_area.cols = 5

        self.connect_area.add_widget(Label(text="Port: "))
        self.port = TextInput(text="COM4", multiline=False)
        self.connect_area.add_widget(self.port)

        self.connect_area.add_widget(Label(text="Baudrate: "))
        self.baud = TextInput(text="115200", multiline=False)
        self.connect_area.add_widget(self.baud)

        self.submit = Button(text="connect", font_size=20)
        self.submit.bind(on_press=self.connect)
        self.connect_area.add_widget(self.submit)

        self.add_widget(self.connect_area)

    def init_file_area(self):
        self.file_status_area = GridLayout()
        self.file_status_area.cols = 1
        self.file_status_area.disabled = False
        # self.gcode_file_path = TextInput(
        #    text="H:\cursor\data\experiments\composition57\gcode\composition57_de7c4e2b608a403be7a96e077f6aeab5.nc",
        #    multiline=False,
        # )
        self.find_button = Button(text="find", font_size=20)
        self.find_button.bind(on_press=self.find)

        self.file_status_area.add_widget(self.find_button)
        self.add_widget(self.file_status_area)

    def init_preview_area(self):
        self.preview_area = GridLayout()
        self.preview_area.cols = 4
        self.preview_area.disabled = True
        self.add_widget(self.preview_area)

    def init_stream_area(self):
        self.start_pause_area = GridLayout()
        self.start_pause_area.cols = 5
        self.start_pause_area.disabled = True
        self.calib = Button(text="calib", font_size=20)
        self.calib.bind(on_press=self._calib)
        self.start_pause_area.add_widget(self.calib)
        self.start = Button(text="start", font_size=20)
        self.start.bind(on_press=self._start)
        self.start_pause_area.add_widget(self.start)
        self.pause = Button(text="stop/pause", font_size=20)
        self.pause.bind(on_press=self._pause)
        self.start_pause_area.add_widget(self.pause)
        self.resume = Button(text="resume", font_size=20)
        self.resume.bind(on_press=self._resume)
        self.start_pause_area.add_widget(self.resume)
        self.add_widget(self.start_pause_area)

        self.progress = ProgressBar(max=1000)
        self.add_widget(self.progress)

    def find(self, instance):
        bl = BoxLayout()
        self.fs = FileChooserListView(path=".")
        bl.add_widget(self.fs)

        self.load = Button(text="load", font_size=20)
        self.load.bind(on_press=self.ffind)
        bl.add_widget(self.load)

        self._popup = Popup(
            title="Load file", content=bl, size_hint=(0.9, 0.9), auto_dismiss=False
        )
        self._popup.open()

    def ffind(self, el):
        path = self.fs.selection[0]
        print(self.fs.selection)
        self.dismiss_popup()

        abspath = pathlib.Path(path)

        if not abspath.is_file():
            log.warn("Not a file..")
            return
        else:
            log.good(f"Loaded {path}")

        c = None
        with open(abspath.as_posix()) as content:
            c = content.readlines()
        log.good(f"lines: {len(c)}")

        self.progress.max = len(c)

    def dismiss_popup(self):
        self._popup.dismiss()

    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)

        self.init_connect_area()
        self.init_file_area()
        self.init_preview_area()
        self.init_stream_area()

    def _start(self, instance):
        self.machine.stream(self.gcode_file_path.text)

    def _calib(self, instance):
        self.machine.calib()

    def _pause(self, instance):
        self.machine.feed_hold()

    def _resume(self, instance):
        self.machine.resume()

    def connect(self, instance):
        _connected = self.machine.connected()
        if not _connected:
            _connected = self.machine.connect(self.port.text, self.baud.text)
            self.submit.text = "disconnect"
        else:
            self.machine.disconnect()
            _connected = False
            self.submit.text = "connect"
        self.preview_area.disabled = not _connected
        self.file_status_area.disabled = not _connected
        self.start_pause_area.disabled = not _connected
        self.start_pause_area.disabled = not _connected

    def simulate_progress(self):
        for i in range(self.progress.max):
            self.progress.value = i
            time.sleep(0.00001)


class MyApp(App):
    def build(self):
        return MyGrid()


def main():
    MyApp().run()


if __name__ == "__main__":
    main()
