from __future__ import annotations

import pathlib
import random
import typing

import arcade
import pymsgbox
import wasabi
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIOnChangeEvent, UIAnchorWidget

from cursor.collection import Collection
from cursor.data import DataDirHandler, DateHandler
from cursor.path import Path
from cursor.position import Position

log = wasabi.Printer()


class RealtimeRenderer(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width=width, height=height, title=title, antialiasing=True, samples=16)
        arcade.set_background_color(arcade.color.GRAY)
        self.__title = title
        self.colors = [
            (color, getattr(arcade.color, color))
            for color in dir(arcade.color)
            if not color.startswith("__")
        ]

        self.shapes = None
        self.collection = Collection()
        self.points = []
        self.clear_list()

        self.cbs = {}
        self.pressed = {}
        self.long_press = {}
        self._on_mouse = None
        self._draw_gui = True
        self.render_points = False

        self.add_cb(arcade.key.S, self.screenshot, False)
        self.add_cb(arcade.key.F, self.enter_fullscreen, False)
        self.add_cb(arcade.key.G, self.toggle_gui, False)

        self.background = None

        self.manager = UIManager()
        self.manager.enable()

        self.camera = arcade.Camera(width, height)

    def screenshot(self, rr: RealtimeRenderer):
        folder = DataDirHandler().jpg(f"{self.title}")
        suffix = pymsgbox.prompt("suffix", default="")
        fn = folder / f"{DateHandler().utc_timestamp()}_{suffix}.png"
        folder.mkdir(parents=True, exist_ok=True)
        log.good(f"saving {fn.as_posix()}")
        try:
            arcade.get_image(0, 0, self.width, self.height).save(fn.as_posix(), "PNG")
        except ValueError as ve:
            log.fail(f"Couldn't get image {ve}")
        except OSError as oe:
            log.fail(f"Couldn't get image {oe}")
        finally:
            pass

    def enter_fullscreen(self, rr: RealtimeRenderer):
        self.set_fullscreen(not self.fullscreen)

    def toggle_gui(self, rr: RealtimeRenderer):
        self._draw_gui = not self._draw_gui

    def set_bg(self, p: pathlib.Path):
        self.background = arcade.load_texture(p)

    def add_slider(self, cb_func: typing.Callable[[float], None], x=50, y=50):
        ui_slider = UISlider(x=x, y=y, value=50, width=300, height=20)

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            # print(ui_slider.value)
            cb_func(ui_slider.value)
            # label.text = f"{ui_slider.value:02.0f}"
            # label.fit_content()

        self.manager.add(UIAnchorWidget(child=ui_slider, align_y=y))

    def set_bg_color(self, col: arcade.color = None):
        if col:
            arcade.set_background_color(col)
        else:
            arcade.set_background_color(random.choice(self.colors)[1])

    @staticmethod
    def run():
        arcade.enable_timings(100)
        arcade.run()

    @property
    def title(self):
        return self.__title

    def set_on_mouse_cb(self, cb: typing.Callable):
        self._on_mouse = cb

    def add_cb(self, key: arcade.key, cb: typing.Callable, long_press: bool = True):
        self.cbs[key] = cb
        self.pressed[key] = False
        self.long_press[key] = long_press

    def clear_list(self):
        self.shapes = arcade.ShapeElementList()
        self.collection = Collection()
        self.points.clear()

    def add_point(self, po: Position, width: int = 5, color: arcade.color = None):
        if not color:
            color = random.choice(self.colors)[1]
        self.points.append(po)
        point = arcade.create_ellipse(po.x, po.y, width, width, color)
        self.shapes.append(point)

    def add_path(self, p: Path, line_width: float = 5, color: arcade.color = None):
        if not color:
            color = random.choice(self.colors)[1]

        line_strip = arcade.create_line_strip(p.as_tuple_list(), color, line_width)
        self.shapes.append(line_strip)

        if self.render_points:
            for point in p:
                self.add_point(point, 50, arcade.color.BLACK)

        self.collection.add(p)

    def add_polygon(self, p: Path, color: arcade.color = None):
        if not color:
            color = random.choice(self.colors)[1]

        self.shapes.append(arcade.create_polygon(p.as_tuple_list(), color))

    def add_collection(
            self, c: Collection, line_width: float = 5, color: arcade.color = None
    ):
        if not color:
            color = random.choice(self.colors)[1]
        [self.add_path(p, line_width, color) for p in c]

    def on_draw(self):
        self.clear()

        self.camera.use()

        if self.background:
            arcade.draw_lrwh_rectangle_textured(0, 0, self.width, self.height, self.background)

        self.shapes.draw()
        if self._draw_gui:
            self.manager.draw()

    def on_update(self, delta_time: float):
        super().update(delta_time)

        fps = int(arcade.get_fps())
        caption = f"{self.__title} fps: {fps} shapes: {len(self.shapes)}"
        self.set_caption(caption)

        for k, v in self.pressed.items():
            if v:
                self.cbs[k](self)
                if not self.long_press[k]:
                    self.pressed[k] = False

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            arcade.exit()
        elif key == arcade.key.C:
            self.clear_list()

        for k, v in self.cbs.items():
            if key == k:
                self.pressed[k] = True

    def on_key_release(self, key: int, modifiers: int):
        for k, v in self.cbs.items():
            if key == k:
                self.pressed[k] = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self._on_mouse:
            self._on_mouse(self, x, y, dx, dy)
