from cursor.device import DrawingMachine

import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

kivy.require("2.0.0")


class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.machine = DrawingMachine()
        self.cols = 1
        self.inside = GridLayout()
        self.inside.cols = 2

        self.inside.add_widget(Label(text="Port: "))
        self.port = TextInput(text="COM4", multiline=False)
        self.inside.add_widget(self.port)

        self.inside.add_widget(Label(text="Baudrate: "))
        self.baud = TextInput(text="12500", multiline=False)
        self.inside.add_widget(self.baud)

        self.add_widget(self.inside)

        self.submit = Button(text="connect", font_size=20)
        self.submit.bind(on_press=self.connect)
        self.add_widget(self.submit)

    def connect(self, instance):
        self.machine.connect(self.port.text, self.baud.text)


class MyApp(App):
    def build(self):
        return MyGrid()


def main():
    MyApp().run()


if __name__ == "__main__":
    main()
