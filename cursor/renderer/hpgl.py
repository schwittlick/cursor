from __future__ import annotations

import pathlib
import logging

from cursor.collection import Collection
from cursor.hpgl.hpgl import HPGL
from cursor.renderer import BaseRenderer
from cursor.timer import Timer


class HPGLRenderer(BaseRenderer):
    def __init__(
        self,
        folder: pathlib.Path,
        auto_pen_ops: int | None = None,
        acceleration: int | None = None,
        travel_acceleration: int | None = None,
    ) -> None:
        super().__init__(folder)

        self.__save_path = folder
        self.auto_pen_ops = auto_pen_ops
        self.acceleration = acceleration
        self.travel_acceleration = travel_acceleration

    def estimated_duration(self, speed) -> int:
        s = 0
        for p in self.collection:
            mm = p.distance / 400  # for hp plotters its 40
            seconds = mm / speed * 10
            s += seconds
        return s

    def optimize(self):
        """
        split by pen select and TSP on separated collections
        """

        timer = Timer()

        collections_split_by_pen = [Collection() for _ in range(8)]
        for pa in self.collection:
            collections_split_by_pen[pa.pen_select - 1].add(pa.copy())

        optimized = Collection()

        for c in collections_split_by_pen:
            if len(c) > 1:
                c.fast_tsp(False, 5)
            optimized += c

        timer.print_elapsed("Optimizing done")
        self.collection = optimized

    @staticmethod
    def generate_string(
        collection: Collection,
        auto_pen_ops: int | None = None,
        acceleration: int | None = None,
        travel_acceleration: int | None = None,
    ) -> str:
        """
        acceleration is the AS for pen-down moves (a path's own acceleration property wins),
        travel_acceleration the AS for the pen-up moves between paths. Both are modal, so
        they are only re-sent when they change.
        """
        _hpgl = HPGL()

        _prev_line_type = 0
        _prev_velocity = 0
        _prev_force = 0
        _prev_pen = 0
        _prev_acceleration = None

        _hpgl.IN()
        if auto_pen_ops is not None:
            _hpgl.AP(auto_pen_ops)
        if acceleration is not None:
            _hpgl.AS(acceleration)
            _prev_acceleration = acceleration

        for p in collection:
            x = p.start_pos().x
            y = p.start_pos().y

            _ps = p.pen_select
            if _prev_pen != _ps:
                if _ps:
                    _hpgl.SP(_ps)
                    _prev_pen = _ps

            _lt = p.line_type
            if _lt:
                if _prev_line_type != _lt:
                    _hpgl.LT(_lt)
                    _prev_line_type = _lt

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

            _lt = p.line_type
            if _lt:
                if _prev_line_type != _lt:
                    _hpgl.LT(_lt)
                    _prev_line_type = _lt

            if p.laser_pwm:
                _hpgl.custom(f"PWM{p.laser_pwm};")

            if p.laser_volt:
                _hpgl.custom(f"VOLT{p.laser_volt:.3};")

            if p.laser_delay:
                _hpgl.custom(f"DELAY{p.laser_delay:.3};")

            if p.laser_amp:
                _hpgl.custom(f"AMP{p.laser_amp:.3};")

            if travel_acceleration is not None and travel_acceleration != _prev_acceleration:
                _hpgl.AS(travel_acceleration)
                _prev_acceleration = travel_acceleration

            _hpgl.PA(int(x), int(y))
            if p.is_polygon:
                _hpgl.custom("PM0;")

            _as = p.acceleration if p.acceleration is not None else acceleration
            if _as is not None and _as != _prev_acceleration:
                _hpgl.AS(_as)
                _prev_acceleration = _as

            _hpgl.PD()

            if p.rgb_led_color:
                _hpgl.custom(f"\nRGB{p.rgb_led_color[0]},{p.rgb_led_color[1]},{p.rgb_led_color[2]};")

            for point in p.vertices[1:]:
                x = point.x
                y = point.y

                _hpgl.PA(int(x), int(y))

            if p.rgb_led_color:
                _hpgl.custom("\nRGB0,0,0;")

            _hpgl.PU()

            if p.is_polygon:
                _hpgl.custom("PM2;")  # switch to PM2; to close and safe
                _hpgl.custom("FP;")

        if travel_acceleration is not None and travel_acceleration != _prev_acceleration:
            _hpgl.AS(travel_acceleration)
        _hpgl.PA(0, 0)
        _hpgl.SP(0)

        return _hpgl.data

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".hpgl")

        _hpgl_string = HPGLRenderer.generate_string(
            self.collection, self.auto_pen_ops, self.acceleration, self.travel_acceleration
        )

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
