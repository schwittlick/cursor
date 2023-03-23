import arcade
import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIOnChangeEvent

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
        self.plotter.thread.add(self.plotter.init)
        self.plotter.thread.resume()


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(1000, 600, "OCTET 2023", resizable=True)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout(vertical=True)

        self.plotters = None

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
        elif key == arcade.key.S:
            for p in self.plotters:
                p.connect()
                p.open_serial()
            pass

        if not self.plotters:
            logger.fail("Plotters not in main gui thread yet")
            return
        for plotter in self.plotters:
            if not plotter.thread:
                logger.warn(f"Ignored keypres bc plotter thread is not ready")
                continue
            if key == arcade.key.P:
                plotter.thread.add(plotter.go_up_down)
            elif key == arcade.key.L:
                # for i in range(4):
                plotter.thread.add(plotter.draw_random_line)
            elif key == arcade.key.O:
                logger.info(f"only sending pen up down to hp7475")
                if plotter.type == PlotterType.HP_7475A_A3:
                    plotter.thread.add(plotter.pen_down_up)
            elif key == arcade.key.R:
                plotter.thread.add(plotter.random_pos)
            elif key == arcade.key.I:
                plotter.thread.add(plotter.init)
            elif key == arcade.key.C:
                plotter.thread.add(plotter.c73)
            elif key == arcade.key.M:
                plotter.thread.add(plotter.mouse)

            plotter.thread.resume()

    def add_labels(self):
        container = arcade.gui.UIBoxLayout(vertical=False)

        button_width = 100
        container.add(arcade.gui.UIFlatButton(text=f"plotter️", width=150, ))
        container.add(arcade.gui.UIFlatButton(text=f"queue", width=button_width, ))
        container.add(arcade.gui.UIFlatButton(text=f"speed", width=button_width, ))
        container.add(arcade.gui.UIFlatButton(text=f"pen", width=button_width, ))
        container.add(arcade.gui.UIFlatButton(text=f"v1", width=button_width, ))
        container.add(arcade.gui.UIFlatButton(text=f"v2", width=button_width, ))
        container.add(arcade.gui.UIFlatButton(text=f"line dist", width=button_width, ))

        self.add(container)

    def render_plotters(self):
        for plo in self.plotters:
            button_width = 100
            container = arcade.gui.UIBoxLayout(vertical=False)
            tb1 = TestButton(text=f"{plo.type}", width=150, plotter=plo, col=all_paths)
            plo.thread.button = tb1
            container.add(tb1)

            def second_clicked(event):
                _plo = event.source.plotter
                _plo.thread.add(_plo.go_up_down)
                _plo.thread.resume()

            def third_clicked(event):
                _plo = event.source.plotter
                _plo.thread.add(_plo.c73)
                _plo.thread.resume()

            def penupdown_clicked(event):
                _plo = event.source.plotter
                _plo.thread.add(_plo.draw_random_line)
                _plo.thread.resume()

            def penupdown_clicked2(event):
                _plo = event.source.plotter
                _plo.thread.add(_plo.pen_up_down)
                _plo.thread.resume()

            def clear_queue(event):
                _plo = event.source.plotter
                _plo.thread.clear()
                _plo.thread.add(_plo.reset)
                _plo.thread.resume()

            #tb2 = arcade.gui.UIFlatButton(text=f"⬆⬇️️ page", width=button_width, )
            #tb2.plotter = plo
            #tb2.on_click = second_clicked
            #container.add(tb2)

            #tb3 = arcade.gui.UIFlatButton(text=f"c73", width=button_width, )
            #tb3.plotter = plo
            #tb3.on_click = third_clicked
            #container.add(tb3)

            #pud = arcade.gui.UIFlatButton(text=f"🃏", width=button_width, )
            #pud.plotter = plo
            #pud.on_click = penupdown_clicked
            #container.add(pud)

            #pud2 = arcade.gui.UIFlatButton(text=f"⬆⬇️️ pen", width=button_width, )
            #pud2.plotter = plo
            #pud2.on_click = penupdown_clicked2
            #container.add(pud2)

            tb4 = arcade.gui.UIFlatButton(text=f"↔️", width=button_width, )
            tb4.plotter = plo
            tb4.on_click = clear_queue
            plo.thread.thread_count = tb4
            container.add(tb4)

            tb5 = arcade.gui.UIFlatButton(text=f"40", width=button_width, )
            tb5.plotter = plo
            # tb5.on_click = clear_queue
            plo.thread.speed_label = tb5
            container.add(tb5)

            tb6 = arcade.gui.UIFlatButton(text=f"0", width=button_width, )
            tb6.plotter = plo
            # tb5.on_click = clear_queue
            plo.thread.pen_label = tb6
            container.add(tb6)

            tb7 = arcade.gui.UIFlatButton(text=f"0", width=button_width, )
            tb7.plotter = plo
            # tb5.on_click = clear_queue
            plo.thread.remaining_seconds_label = tb7
            #container.add(tb7)

            v1_button = arcade.gui.UIFlatButton(text=f"0", width=button_width, )
            v1_button.plotter = plo
            plo.thread.v1_label = v1_button
            container.add(v1_button)

            v2_button = arcade.gui.UIFlatButton(text=f"1000", width=button_width, )
            v2_button.plotter = plo
            plo.thread.v2_label = v2_button
            container.add(v2_button)

            ld_button = arcade.gui.UIFlatButton(text=f"10", width=button_width, )
            ld_button.plotter = plo
            plo.thread.line_distance_label = ld_button
            container.add(ld_button)

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
