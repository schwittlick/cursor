from __future__ import annotations

import pathlib
from tqdm import tqdm
import logging

from cursor.hpgl.hpgl import HPGL
from cursor.renderer import BaseRenderer


class HPGLRenderer(BaseRenderer):
    def __init__(
        self,
        folder: pathlib.Path,
        layer_pen_mapping: dict = None,
        line_type_mapping: dict = None,
    ) -> None:
        super().__init__(folder)

        self.__save_path = folder
        self.__layer_pen_mapping = layer_pen_mapping
        self.__line_type_mapping = line_type_mapping

    def estimated_duration(self, speed) -> int:
        s = 0
        for p in self.paths:
            mm = p.distance / 400  # for hp plotters its 40
            seconds = mm / speed * 10
            s += seconds
        return s

    def generate_string(self):
        _hpgl = HPGL()

        # _prev_line_type = 0
        _prev_velocity = 0
        _prev_force = 0
        _prev_pen = 0

        _hpgl.PU()

        with tqdm(total=len(self.paths)) as pbar:
            pbar.update(0)
            for p in self.paths:
                x = p.start_pos().x
                y = p.start_pos().y

                _ps = p.pen_select
                if _prev_pen != _ps:
                    if _ps:
                        _hpgl.SP(_ps)
                        _prev_pen = _ps

                # if p.line_type:
                #     if _prev_line_type != p.line_type:
                #         _hpgl_string += f"LT{self.__linetype_from_layer(p.line_type)};"
                #         _prev_line_type = p.line_type

                _v = p.velocity
                if _prev_velocity != _v:
                    if _v:
                        _hpgl.VS(_v)
                        _prev_velocity = _v

                _fs = p.pen_force
                if _fs:
                    if _prev_force != _fs:
                        _hpgl.FS(_fs)
                        _prev_force = _fs

                if p.laser_pwm:
                    _hpgl.custom(f"PWM{p.laser_pwm};")

                if p.laser_volt:
                    _hpgl.custom(f"VOLT{p.laser_volt:.3};")

                if p.laser_delay:
                    _hpgl.custom(f"DELAY{p.laser_delay:.3};")

                if p.laser_amp:
                    _hpgl.custom(f"AMP{p.laser_amp:.3};")

                _hpgl.PA(int(x), int(y))
                if p.is_polygon:
                    _hpgl.custom("PM0;")

                _hpgl.PD()

                for point in p.vertices:
                    x = point.x
                    y = point.y

                    _hpgl.PA(int(x), int(y))

                _hpgl.PU()

                if p.is_polygon:
                    _hpgl.custom("PM2;")  # switch to PM2; to close and safe
                    _hpgl.custom("FP;")

                pbar.update(1)

        _hpgl.PA(0, 0)
        _hpgl.SP(0)

        return _hpgl.data

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".hpgl")

        _hpgl_string = self.generate_string()

        with open(fname.as_posix(), "w") as file:
            file.write(_hpgl_string)

        logging.info(f"Finished saving {fname.name}")
        logging.info(f"in {self.__save_path}")

        return _hpgl_string

    @staticmethod
    def __get_pen_select(pen_select: int | None) -> int:
        if pen_select is None:
            return 1

        return pen_select

    def __pen_from_layer(self, layer: str | None = None) -> int:
        if self.__layer_pen_mapping is None:
            return 1

        if layer not in self.__layer_pen_mapping.keys():
            return 1

        return self.__layer_pen_mapping[layer]

    def __linetype_from_layer(self, linetype: int | None = None) -> str:
        _default_linetype = ""
        if self.__line_type_mapping is None:
            return _default_linetype

        if linetype not in self.__line_type_mapping.keys():
            return _default_linetype

        return self.__line_type_mapping[linetype]

    @staticmethod
    def __get_velocity(velocity: int | None = None) -> int:
        if velocity is None:
            return 110

        return velocity

    @staticmethod
    def __get_pen_force(pen_force: int | None = None) -> int:
        if pen_force is None:
            return 16

        return pen_force
