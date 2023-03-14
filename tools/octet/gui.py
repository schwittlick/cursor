import socket

import arcade
import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIOnChangeEvent, UILabel

import wasabi

from tools.octet.data import all_paths
from tools.octet.plotter import Plotter

logger = wasabi.Printer(pretty=True, no_print=False)


class TestButton(arcade.gui.UIFlatButton):
    def __init__(self, plotter, col, **kwargs):
        super().__init__(**kwargs)
        self.plotter = plotter
        self.col = col

    def on_click(self, event: arcade.gui.UIOnClickEvent):
        logger.info(self.plotter)
        self.plotter.thread.add(Plotter.init)
        self.plotter.thread.resume()


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "OCTET 2023", resizable=True)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout(vertical=True)

    def render_plotters(self, plotters):
        for plo in plotters:
            container = arcade.gui.UIBoxLayout(vertical=False)
            tb1 = TestButton(text=f"{plo.type}", width=100, plotter=plo, col=all_paths)
            plo.thread.button = tb1
            container.add(tb1)

            def second_clicked(event):
                plo.thread.add(Plotter.random_pos)
                plo.thread.resume()

            def third_clicked(event):
                plo.thread.add(Plotter.draw_random_line)
                plo.thread.resume()

            tb2 = arcade.gui.UIFlatButton(text=f"random_pos", width=100, )
            tb2.on_click = second_clicked
            container.add(tb2)

            tb3 = arcade.gui.UIFlatButton(text=f"random_line", width=100, )
            tb3.on_click = second_clicked
            container.add(tb3)

            lab = UILabel(text="0")
            plo.thread.label = lab
            container.add(lab)
            self.add(container)

            def update_label(t):
                lab.text = str(t)

            def set_label(t):
                arcade.schedule(lambda dt: update_label(t), interval=0)
                arcade.unschedule(lambda dt: update_label(t))

            plo.thread.set_cb(set_label)

    def add(self, button):
        self.v_box.add(button)

    def add_slider(self, f):
        slider = UISlider(
            text="global_speed",
            center_x=300,
            center_y=100,
            height=50,
            min_value=1,
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
