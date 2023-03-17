import socket

import arcade
import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIOnChangeEvent, UILabel

import wasabi

from cursor.device import PlotterType
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
        super().__init__(1000, 600, "OCTET 2023", resizable=True)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout(vertical=True)

        self.plotter = None

    # Define the key press callback function
    def on_key_press(self, key, modifiers):
        if key == arcade.key.F:
            self.set_fullscreen(not self.fullscreen)
            width, height = self.get_size()
            self.set_viewport(0, width, 0, height)
            return
        elif key == arcade.key.Q:
            arcade.exit()
            return

        if not self.plotters:
            logger.fail("Plotters not in main gui thread yet")
            return
        for plotter in self.plotters:
            if not plotter.thread:
                logger.warn(f"Ignored keypres bc plotter thread is not ready")
                continue
            if key == arcade.key.P:
                plotter.thread.add(Plotter.go_up_down)
            elif key == arcade.key.L:
                # for i in range(4):
                plotter.thread.add(Plotter.draw_random_line)
            elif key == arcade.key.O:
                logger.info(f"only sending pen up down to hp7475")
                if plotter.type == PlotterType.HP_7475A_A3:
                    plotter.thread.add(Plotter.pen_down_up)
            elif key == arcade.key.R:
                plotter.thread.add(Plotter.random_pos)
            elif key == arcade.key.S:
                plotter.thread.add(Plotter.set_speed)
            elif key == arcade.key.I:
                plotter.thread.add(Plotter.init)
            elif key == arcade.key.C:
                plotter.thread.add(Plotter.c73)

            plotter.thread.resume()

    def render_plotters(self, plotters):
        for plo in plotters:
            container = arcade.gui.UIBoxLayout(vertical=False)
            tb1 = TestButton(text=f"{plo.type}", width=300, plotter=plo, col=all_paths)
            plo.thread.button = tb1
            container.add(tb1)

            def second_clicked(event):
                _plo = event.source.plotter
                _plo.thread.add(Plotter.random_pos)
                _plo.thread.resume()

            def third_clicked(event):
                _plo = event.source.plotter
                _plo.thread.add(Plotter.draw_random_line)
                _plo.thread.resume()

            def penupdown_clicked(event):
                _plo = event.source.plotter
                _plo.thread.add(Plotter.pen_down_up)
                _plo.thread.resume()

            tb2 = arcade.gui.UIFlatButton(text=f"pos", width=100, )
            tb2.plotter = plo
            tb2.on_click = second_clicked
            container.add(tb2)

            tb3 = arcade.gui.UIFlatButton(text=f"line", width=100, )
            tb3.plotter = plo
            tb3.on_click = third_clicked
            container.add(tb3)

            pud = arcade.gui.UIFlatButton(text=f"pen up down", width=100, )
            pud.plotter = plo
            pud.on_click = penupdown_clicked
            container.add(pud)

            tb4 = arcade.gui.UIFlatButton(text=f"threads", width=100, )
            tb4.plotter = plo
            # tb4.on_click = second_clicked
            plo.thread.thread_count = tb4
            container.add(tb4)

            self.add(container)

            # optional complete cb
            # plo.thread.set_cb(set_label)

    def add(self, button):
        self.v_box.add(button)

    def add_slider(self, f):
        slider = UISlider(
            text="speed_all",
            center_x=300,
            center_y=100,
            height=50,
            min_value=1,
            max_value=110,
            value=40,
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
