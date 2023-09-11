from __future__ import annotations

import pathlib
import random
import typing

import arcade
import pymsgbox
import wasabi
from arcade.experimental import RenderTargetTexture, postprocessing
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIOnChangeEvent, UILabel

from cursor.collection import Collection
from cursor.data import DataDirHandler, DateHandler
from cursor.path import Path
from cursor.position import Position

log = wasabi.Printer()


class Buffer(RenderTargetTexture):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D texture0;

            in vec2 uv;
            out vec4 fragColor;

            void main() {
                vec4 color = texture(texture0, uv);
                fragColor = color;
            }
            """,
        )

    def use(self):
        self._fbo.use()

    def draw(self):
        self.texture.use(0)
        self._quad_fs.render(self.program)


class RealtimeRenderer(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(
            width=width, height=height, title=title, antialiasing=True, samples=16
        )
        arcade.set_background_color(arcade.color.GRAY)
        self.__title = title
        self.colors = [
            (color, getattr(arcade.color, color))
            for color in dir(arcade.color)
            if not color.startswith("__")
        ]

        self.frame_count = 0

        self.shapes = arcade.ShapeElementList()
        self.collection = Collection()
        self._points = []
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

        self._background = None

        self.manager = UIManager()
        self.manager.enable()

        self.camera = arcade.Camera(width, height)

        bloom = self.bloom()
        self.bloom_color_attachment = bloom[0]
        self.bloom_screen = bloom[1]
        self.bloom_postprocessing = bloom[2]

    def bloom(self):
        bloom_color_attachment = self.ctx.texture((self.width, self.height))
        bloom_screen = self.ctx.framebuffer(color_attachments=[bloom_color_attachment])

        kernel_size = 1
        sigma = 5
        mu = 0
        step = 0
        # Control the intensity
        multiplier = 1

        # Create a post-processor to create a bloom
        return (
            bloom_color_attachment,
            bloom_screen,
            postprocessing.BloomEffect(
                (self.width, self.height), kernel_size, sigma, mu, multiplier, step
            ),
        )

    @property
    def points(self) -> list[Position]:
        return self._points

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
        self._background = arcade.load_texture(p)

    def add_slider(
        self,
        cb_func: typing.Callable[[float], None],
        name: str,
        value: int,
        min_value: int,
        max_value: int,
        x: int = 50,
        y: int = 50,
        w: int = 500,
        h: int = 30,
        text_color=arcade.color.GRAY,
    ):
        ui_slider = UISlider(
            x=x,
            y=y,
            value=value,
            min_value=min_value,
            max_value=max_value,
            width=w,
            height=h,
        )
        ui_label = UILabel(x=x + w, y=y, text=f"{name}: {value}", text_color=text_color)

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            cb_func(ui_slider.value)
            ui_label.text = f"{name}: {ui_slider.value:02.0f}"
            ui_label.fit_content()

        # self.manager.add(UIAnchorWidget(child=ui_slider, align_y=y))
        self.manager.add(ui_slider)
        self.manager.add(ui_label)

    def background(self, col: arcade.color = None):
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

    def add_cb(self, key: arcade.key, cb: typing.Callable, long_press: bool = False):
        self.cbs[key] = cb
        self.pressed[key] = False
        self.long_press[key] = long_press

    def clear_list(self):
        self.shapes = arcade.ShapeElementList()
        self.collection = Collection()
        self._points.clear()

    def add_point(self, po: Position, width: int = 5, color: arcade.color = None):
        if not color:
            color = random.choice(self.colors)[1]
        self._points.append(po)
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

        if self._background:
            arcade.draw_lrwh_rectangle_textured(
                0, 0, self.width, self.height, self._background
            )

        self.bloom_screen.use()
        self.bloom_screen.clear((0, 0, 0, 0))

        self.shapes.draw()

        # todo: add list of shaders that can be added/removed at runtime
        # self.bloom_postprocessing.render(self.bloom_color_attachment, self)
        if self._draw_gui:
            self.manager.draw()

        self.frame_count += 1

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
