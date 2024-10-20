from __future__ import annotations

import collections
import copy
import hashlib
import math
import sys
import typing

import numpy as np
import pandas as pd
import shapely
from scipy import spatial
from scipy import stats
from shapely import union_all, Polygon
from shapely.geometry import LineString, MultiLineString, JOIN_STYLE, Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import clip_by_rect
from skimage.transform import estimate_transform

from cursor import misc
from cursor.algorithm import ramer_douglas_peucker
from cursor.algorithm.entropy import calc_entropy
from cursor.algorithm.frechet import LinearDiscreteFrechet
from cursor.algorithm.frechet import euclidean
from cursor.bb import BoundingBox
from cursor.misc import apply_matrix, clamp, line_intersection
from cursor.properties import Property
from cursor.position import Position

import logging

from cursor.timer import timing


class Path:
    def __init__(
            self, vertices: list[Position] | None = None, properties: dict | None = None
    ) -> None:
        self._vertices: list[Position] = []
        self.properties = {
            Property.LAYER: "layer1",
            Property.COLOR: (0, 0, 0),
            Property.WIDTH: 1,
            Property.TAGS: []
        }

        if vertices is not None:
            self._vertices = vertices

        if properties is not None:
            self.properties.update(properties)

            if Property.COLOR not in self.properties.keys():
                self.color = (0, 0, 0)
            if Property.WIDTH not in self.properties.keys():
                self.width = 1

    def __repr__(self) -> str:
        rep = (
            f"vertices: {len(self.vertices)} "
            f"bb: {self.bb()}"
            f"properties: {self.properties}"
        )
        return rep

    def __eq__(self, other: Path) -> bool:
        if len(self) != len(other):
            return False

        if self.properties != other.properties:
            return False

        for i in range(len(self)):
            if self.vertices[i] != other[i]:
                return False

        return True

    def __hash__(self) -> int:
        return hash(repr(self))

    def __len__(self) -> int:
        return len(self.vertices)

    def __iter__(self) -> typing.Iterator[Position]:
        for v in self.vertices:
            yield v

    def __getitem__(self, item: int) -> Position:
        return self._vertices[item]

    def as_tuple_list(self) -> list[tuple[float, float]]:
        return [v.as_tuple() for v in self.vertices]

    def as_array(self) -> np.ndarray:
        return np.array([p.as_array() for p in self.vertices])

    def as_dataframe(self) -> pd.DataFrame:
        arr = self.as_array()
        return pd.DataFrame(arr, columns=["x", "y"])

    @classmethod
    def from_tuple_list(cls, tuple_list: list[tuple[float, float]]) -> Path:
        return Path([Position.from_tuple(p) for p in tuple_list])

    @classmethod
    def from_list(cls, positions: list[Position]) -> Path:
        _pa = Path()
        for pa in positions:
            _pa.add_position(pa)
        return _pa

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self.vertices).encode("utf-8")).hexdigest()

    @property
    def vertices(self) -> list[Position]:
        return self._vertices

    @vertices.setter
    def vertices(self, vertices: list[Position]) -> None:
        self._vertices = vertices

    @property
    def line_type(self) -> tuple[int, int] | None:
        if Property.LINE_TYPE not in self.properties.keys():
            return None

        return self.properties[Property.LINE_TYPE]

    @line_type.setter
    def line_type(self, line_type: tuple[int, int]) -> None:
        self.properties[Property.LINE_TYPE] = line_type

    @property
    def layer(self) -> str | None:
        if Property.LAYER not in self.properties.keys():
            return None

        return self.properties[Property.LAYER]

    @layer.setter
    def layer(self, layer: str) -> None:
        self.properties[Property.LAYER] = layer

    @property
    def pen_force(self) -> int | None:
        if Property.PEN_FORCE not in self.properties.keys():
            return None

        return self.properties[Property.PEN_FORCE]

    @pen_force.setter
    def pen_force(self, pen_force: int) -> None:
        self.properties[Property.PEN_FORCE] = pen_force

    @property
    def pen_select(self) -> int | None:
        if Property.PEN_SELECT not in self.properties.keys():
            return None

        return self.properties[Property.PEN_SELECT]

    @pen_select.setter
    def pen_select(self, pen_select: int) -> None:
        self.properties[Property.PEN_SELECT] = pen_select

    @property
    def velocity(self) -> int | None:
        if Property.VELOCITY not in self.properties.keys():
            return None

        return self.properties[Property.VELOCITY]

    @velocity.setter
    def velocity(self, pen_velocity: int) -> None:
        self.properties[Property.VELOCITY] = pen_velocity

    @property
    def tags(self) -> list[str] | None:
        if Property.TAGS not in self.properties.keys():
            return None

        return self.properties[Property.TAGS]

    @property
    def color(self) -> tuple[int, ...] | None:
        if Property.COLOR not in self.properties.keys():
            return None

        return self.properties[Property.COLOR]

    @color.setter
    def color(self, color: tuple[int, ...]) -> None:
        self.properties[Property.COLOR] = color

    @property
    def width(self) -> float | None:
        if Property.WIDTH not in self.properties.keys():
            return None

        return self.properties[Property.WIDTH]

    @width.setter
    def width(self, width: float) -> None:
        self.properties[Property.WIDTH] = width

    @property
    def laser_pwm(self) -> int | None:
        if Property.LASER_PWM not in self.properties.keys():
            return None

        return self.properties[Property.LASER_PWM]

    @laser_pwm.setter
    def laser_pwm(self, laser_pwm: int) -> None:
        self.properties[Property.LASER_PWM] = laser_pwm

    @property
    def laser_volt(self) -> float | None:
        if Property.LASER_VOLT not in self.properties.keys():
            return None

        return self.properties[Property.LASER_VOLT]

    @laser_volt.setter
    def laser_volt(self, laser_volt: float) -> None:
        self.properties[Property.LASER_VOLT] = laser_volt

    @property
    def laser_amp(self) -> float | None:
        if Property.LASER_AMP not in self.properties.keys():
            return None

        return self.properties[Property.LASER_AMP]

    @laser_amp.setter
    def laser_amp(self, laser_amp: float) -> None:
        self.properties[Property.LASER_AMP] = laser_amp

    @property
    def laser_delay(self) -> float | None:
        if Property.LASER_DELAY not in self.properties.keys():
            return None

        return self.properties[Property.LASER_DELAY]

    @laser_delay.setter
    def laser_delay(self, laser_delay: float) -> None:
        self.properties[Property.LASER_DELAY] = laser_delay

    @property
    def laser_onoff(self) -> bool | None:
        if Property.LASER_ONOFF not in self.properties.keys():
            return None

        return self.properties[Property.LASER_ONOFF]

    @laser_onoff.setter
    def laser_onoff(self, laser_onoff: bool) -> None:
        self.properties[Property.LASER_ONOFF] = laser_onoff

    @property
    def is_polygon(self) -> bool | None:
        if Property.IS_POLY not in self.properties.keys():
            return None

        return bool(self.properties[Property.IS_POLY])

    @is_polygon.setter
    def is_polygon(self, is_polygon: bool) -> None:
        self.properties[Property.IS_POLY] = is_polygon

    def is_closed(self) -> bool:
        assert len(self) > 2
        start = self.start_pos()
        end = self.end_pos()
        x = math.isclose(start.x, end.x)
        y = math.isclose(start.y, end.y)
        return x and y

    def add(self, x: float, y: float, timestamp: int = 0) -> None:
        self.vertices.append(Position(x, y, timestamp))

    def add_position(self, pos: Position) -> None:
        self.vertices.append(pos)

    def clear(self) -> None:
        self.vertices.clear()

    def copy(self) -> Path:
        return Path(
            None if self.empty() else copy.deepcopy(
                self.vertices), copy.deepcopy(self.properties)
        )

    def reverse(self) -> None:
        self.vertices.reverse()

    def reversed(self) -> Path:
        c = copy.deepcopy(self.vertices)
        c.reverse()
        return Path(c, self.properties)

    def start_pos(self) -> Position:
        if len(self.vertices) == 0:
            raise IndexError
        return self.vertices[0]

    def end_pos(self) -> Position:
        if len(self.vertices) == 0:
            raise IndexError

        return self.vertices[-1]

    def bb(self) -> BoundingBox:
        minx = min(self.vertices, key=lambda pos: pos.x).x
        miny = min(self.vertices, key=lambda pos: pos.y).y
        maxx = max(self.vertices, key=lambda pos: pos.x).x
        maxy = max(self.vertices, key=lambda pos: pos.y).y
        b = BoundingBox(minx, miny, maxx, maxy)
        return b

    def oriented_bb(self) -> list[tuple]:
        # returns a list of 5 points that make the four pounts of a rectangle.
        # the first and last point are equal
        line = LineString(self.as_tuple_list())
        rect = list(line.minimum_rotated_rectangle.exterior.coords)
        return rect

    def aspect_ratio(self) -> float | np.inf:
        if len(self) < 2:
            return 0.0

        return self.bb().aspect_ratio()

    @property
    def distance(self) -> float:
        """
        Calculates the summed distance between all points in sequence
        Also known as "travel distance"
        """
        dist = 0

        def calculateDistance(x1, y1, x2, y2) -> float:
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            return dist

        for i in range(len(self.vertices) - 1):
            current = self[i]
            next = self[i + 1]

            d = calculateDistance(current.x, current.y, next.x, next.y)
            dist += d

        return dist

    def translate(self, x: float, y: float) -> None:
        [p.translate(x, y) for p in self.vertices]

    def scale(self, x: float, y: float) -> None:
        [p.scale(x, y) for p in self.vertices]

    def scaled(self, x: float, y: float) -> Path:
        _path = Path()
        _path.properties = self.properties
        _path.vertices = [p.scaled(x, y) for p in self.vertices]
        return _path

    def rot(self, angle: float, origin: tuple[float, float] = (0.0, 0.0)) -> None:
        [p.rot(angle, origin) for p in self.vertices]

    def nearest_points(self, pos: Position) -> Position:
        """
        finds the closest point on the path
        may not be one of the discrete points
        """
        line = LineString(self.as_tuple_list())
        nearest = line.interpolate(line.project(Point(pos.x, pos.y)))
        return Position(nearest.x, nearest.y)

    def dilate_erode(self, dist: float) -> Path:
        """
        erodes with negative dist
        """
        line = LineString(self.as_tuple_list())
        res = line.buffer(dist).exterior.coords
        r = Path()
        [r.add(x, y) for x, y in res]
        return r

    def move_to_origin(self) -> None:
        """
        moves path to zero origin
        after calling this the bb of the path has its x,y at 0,0
        """

        _bb = self.bb()
        if _bb.x < 0:
            self.translate(abs(_bb.x), 0.0)
        else:
            self.translate(-abs(_bb.x), 0.0)

        if _bb.y < 0:
            self.translate(0.0, abs(_bb.y))
        else:
            self.translate(0.0, -abs(_bb.y))

    def fit(self, bb: BoundingBox, padding: float, keep_aspect: bool = False) -> None:
        """
        padding is in % of bounding box scale. weird.
        putting an assert here just in case
        this should be in absolute values
        """
        assert padding < 1

        self.move_to_origin()
        _bb = self.bb()

        _w = _bb.w
        if _w == 0.0:
            _w = 0.001
        _h = _bb.h
        if _h == 0.0:
            _h = 0.001

        xscale = bb.w / _w
        yscale = bb.h / _h
        if not math.isclose(padding, 0.0):
            xscale *= padding
            yscale *= padding

        if keep_aspect:
            if xscale > yscale:
                xscale = yscale
            else:
                yscale = xscale

        # log.info(f"{self.__class__.__name__}: fit: scaled by {xscale:.2f} {yscale:.2f}")
        self.scale(xscale, yscale)

        # _bb = self.bb()

        self.translate(bb.x, bb.y)

    def morph(
            self, start: Position | tuple[float, float], end: Position | tuple[float, float]
    ) -> Path:
        if isinstance(start, Position) and isinstance(end, Position):
            start = (start.x, start.y)
            end = (end.x, end.y)

        path = Path()
        end_np = self.end_pos().as_array()
        start_np = self.start_pos().as_array()
        new_end_np = np.array(end, dtype=float)
        new_start_np = np.array(start, dtype=float)

        for point in self.vertices:
            nparr = point.as_array()

            dir_old = np.subtract(end_np, start_np)
            dir_new = np.subtract(new_end_np, new_start_np)
            mag_diff = np.linalg.norm(dir_new) / np.linalg.norm(dir_old)
            if mag_diff is np.nan:
                mag_diff = 0.0
            if math.isinf(mag_diff):
                mag_diff = 1.0
            nparr = nparr * mag_diff
            path.add(nparr[0], nparr[1], point.timestamp)

        current_end = path.end_pos().as_array()
        current_start = path.start_pos().as_array()
        current_start_to_end = np.subtract(current_end, current_start)

        new_start_to_end = np.subtract(new_end_np, new_start_np)

        current_start_to_end = current_start_to_end / np.linalg.norm(
            current_start_to_end
        )
        new_start_to_end = new_start_to_end / np.linalg.norm(new_start_to_end)

        try:
            angle = np.arccos(
                np.clip(
                    np.dot(current_start_to_end, new_start_to_end), -
                    math.pi, math.pi
                )
            )
        except RuntimeWarning as w:
            logging.error(w)

        # acos can't properly calculate angle more than 180°.
        # solution taken from here:
        # http://www.gamedev.net/topic/556500-angle-between-vectors/
        if (
                current_start_to_end[0] * new_start_to_end[1]
                < current_start_to_end[1] * new_start_to_end[0]
        ):
            angle = 2 * math.pi - angle

        for p in path.vertices:
            p.rot(angle)

        translation = np.subtract(new_start_np, path.start_pos().as_array())
        for p in path.vertices:
            p.translate(translation[0], translation[1])

        return path

    def intersect(self, newpath: Path) -> tuple[bool, float, float]:
        for p1 in range(len(newpath) - 1):
            for p2 in range(len(self) - 1):
                line1Start = newpath[p1]
                line1End = newpath[p1 + 1]
                line2Start = self[p2]
                line2End = self[p2 + 1]

                diffLAx = line1End.x - line1Start.x
                diffLAy = line1End.y - line1Start.y
                diffLBx = line2End.x - line2Start.x
                diffLBy = line2End.y - line2Start.y
                compareA = diffLAx * line1Start.y - diffLAy * line1Start.x
                compareB = diffLBx * line2Start.y - diffLBy * line2Start.x
                if ((diffLAx * line2Start.y - diffLAy * line2Start.x) < compareA) ^ (
                        (diffLAx * line2End.y - diffLAy * line2End.x) < compareA
                ) and ((diffLBx * line1Start.y - diffLBy * line1Start.x) < compareB) ^ (
                        (diffLBx * line1End.y - diffLBy * line1End.x) < compareB
                ):
                    ok = (diffLAx * diffLBy) - (diffLAy * diffLBx)
                    if ok == 0:
                        ok = 0.01
                    lDetDivInv = 1 / ok
                    i_x = -((diffLAx * compareB) -
                            (compareA * diffLBx)) * lDetDivInv
                    i_y = -((diffLAy * compareB) -
                            (compareA * diffLBy)) * lDetDivInv

                    return True, i_x, i_y

        return False, 0.0, 0.0

    def intersect_all(self, newpath: Path) -> list[Position]:
        intersection_points = []

        for p1 in range(len(newpath) - 1):
            for p2 in range(len(self) - 1):
                line1Start = newpath[p1]
                line1End = newpath[p1 + 1]
                line2Start = self[p2]
                line2End = self[p2 + 1]

                intersection = Path.intersect_segment(line1Start.as_tuple(), line1End.as_tuple(),
                                                      line2Start.as_tuple(), line2End.as_tuple())

                if intersection:
                    intersection_points.append(
                        Position.from_tuple(intersection))

        return intersection_points

    def interp(self, newpath: Path, perc: float) -> Path:
        path = Path()

        maxpoint = max(len(newpath), len(self))

        for i in range(maxpoint):
            idxthis = int((float(i) / maxpoint) * len(self))
            idxnew = int((float(i) / maxpoint) * len(newpath))

            pthis = self[idxthis]
            pnew = newpath[idxnew]
            x_interp = misc.mix(pthis.x, pnew.x, perc)
            y_interp = misc.mix(pthis.y, pnew.y, perc)
            time_interp = misc.mix(pthis.timestamp, pnew.timestamp, perc)

            path.add(x_interp, y_interp, int(time_interp))

        return path

    def direction_changes(self, mapped: bool = False) -> list[float]:
        """
        returns a list of radial angles from each point
        mapped: default is output values between -360° and 360°
        if True, mapped from 0 - 360°

        :return: len() = self.__len__() - 1

        """
        angles = []
        idx = 0
        for _ in self.vertices:
            if idx > 0:
                f = self.vertices[idx - 1]
                s = self.vertices[idx]
                ang1 = np.arctan2(*f.as_tuple()[::-1])
                ang2 = np.arctan2(*s.as_tuple()[::-1])
                if mapped:
                    angle = np.rad2deg((ang1 - ang2) % (2 * np.pi))
                else:
                    angle = np.rad2deg(ang1 - ang2)
                angles.append(angle)
            idx += 1

        return angles

    def slopes(self) -> list[float]:
        """
        Calculates and normalizes the slopes of the path. The normalization adjusts
        the slopes by the general slope of the line connecting the start and end points
        of the polyline, compensating for the overall orientation.

        :return: List of normalized slopes for each segment of the polyline
        """

        def cal_slope(p1: Position, p2: Position) -> float:
            return (p1.y - p2.y) / (p1.x - p2.x)

        if len(self.vertices) < 2:
            return []  # Not enough points to form a line

        if self.vertices[0].x == self.vertices[-1].x:
            general_slope = float('inf')
        else:
            general_slope = cal_slope(self.vertices[-1], self.vertices[0])

        normalized_slopes = []
        for i in range(len(self.vertices) - 1):
            if self.vertices[i].x == self.vertices[i + 1].x:
                # Simplify by treating vertical segments as having zero slope
                segment_slope = float('inf')
            else:
                segment_slope = cal_slope(
                    self.vertices[i + 1], self.vertices[i])

            # If both slopes are infinite, the normalized slope is considered 0 (parallel lines)
            if general_slope == float('inf') and segment_slope == float('inf'):
                normalized_slope = 0
            elif general_slope == float('inf'):
                # If only the general slope is infinite, cannot normalize; set as infinite
                normalized_slope = float('inf')
            else:
                normalized_slope = segment_slope - general_slope

            normalized_slopes.append(normalized_slope)
        return normalized_slopes

    @property
    def duration(self) -> int:
        start = self.start_pos().timestamp
        end = self.end_pos().timestamp
        return end - start

    @property
    def entropy_x(self) -> float:
        return calc_entropy([v.x for v in self.vertices])

    @property
    def entropy_y(self) -> float:
        return calc_entropy([v.y for v in self.vertices])

    @property
    def entropy_direction_changes(self) -> float:
        return calc_entropy(self.direction_changes())

    def __differential_entropy_wrap(self, values: list[float]) -> float:
        window_length = None  # max(int(len(values) * 0.1), 1)
        if len(values) < 5:
            logging.error(
                "Can't compute window_length for such small list of values..")
        try:
            de = stats.differential_entropy(
                values,
                window_length=window_length,
            )
            if np.isinf(de):
                # logging.warning(f"Infinite differential entropy.. {self}")
                # logging.warning(f"{self.vertices}")
                return 100.0
            return de

        except ValueError as ve:
            logging.error(f"Failed differential entropy: {ve}")
            logging.error(f"At path {self} for vertices {self.vertices}")
            return 0.0

    @property
    def differential_entropy_x(self) -> float:
        return self.__differential_entropy_wrap([v.x for v in self.vertices])

    @property
    def differential_entropy_y(self) -> float:
        return self.__differential_entropy_wrap([v.y for v in self.vertices])

    def empty(self) -> bool:
        return len(self.vertices) < 1

    def index_of_closest(self, point: tuple[float, float]) -> int:
        assert len(self) > 1
        min_distance = sys.float_info.max
        closest = 0
        for paa in self:
            dist = paa.distance(point)
            if dist < min_distance:
                min_distance = dist
                closest = self.vertices.index(paa)
        assert min_distance != sys.float_info.max
        logging.info(f"mindist: {min_distance}")
        return closest

    def clean(self) -> None:
        """
        removes consecutive duplicates
        """
        prev = Position()

        self.vertices = [
            prev := v for v in self.vertices if prev.x != v.x or prev.y != v.y
        ]  # noqa: F841
        self.vertices = [
            prev := v for v in self.vertices if v.x is not None and v.y is not None
        ]  # noqa: F841
        self.vertices = [
            prev := v for v in self.vertices if v.x is not np.nan and v.y is not np.nan
        ]  # noqa: F841
        self.vertices = [
            prev := v  # noqa: F841
            for v in self.vertices
            if not math.isnan(v.x) and not math.isnan(v.y)
        ]

    def limit(self) -> None:
        """
        removes points larger than 1.0
        """
        self.vertices = [
            v for v in self.vertices if 1.0 >= v.x >= 0.0 and 1.0 >= v.y >= 0.0
        ]

    def similarity(self, _path: Path) -> float:
        """
        this does not really work..

        most similarities are > 0.7, even for severely un-similar
        paths. what might help is to normalize them (and their BB)
        into the space around the (0, 0) origin. but i'm not really
        sure. similarity between a list of coordinates doesn't seem
        to be a trivial thing. especially when you want some meaningful
        results. to be continued. :)
        """
        if len(self) < len(_path):
            diff = len(_path) - len(self)
            _t = self.vertices.copy()
            for i in range(diff):
                _t.append(self.end_pos())
            result = 1 - spatial.distance.cosine(_t, _path.vertices)
            return result[1]

        if len(_path) < len(self):
            diff = len(self) - len(_path)
            _t = _path.vertices.copy()
            for i in range(diff):
                _t.append(_path.end_pos())
            result = 1 - spatial.distance.cosine(self.vertices, _t)
            return result[1]

        result = 1 - spatial.distance.cosine(self.vertices, _path.vertices)
        return result[1]

    def frechet_similarity(self, _path: Path) -> float:
        """
        https://github.com/joaofig/discrete-frechet
        """
        distance = euclidean
        fdfs = LinearDiscreteFrechet(distance)
        return fdfs.distance(self.as_array(), _path.as_array())

    @property
    def variation_x(self) -> float:
        variation_x = stats.variation([v.x for v in self.vertices], ddof=1)
        if np.isnan(variation_x):
            return 0.0
        if np.isinf(variation_x):
            return 100.0
        return float(variation_x)

    @property
    def variation_y(self) -> float:
        variation_y = stats.variation([v.y for v in self.vertices], ddof=1)
        if np.isnan(variation_y):
            return 0.0
        if np.isinf(variation_y):
            return 100.0
        return float(variation_y)

    def centeroid(self) -> tuple[float, float]:
        arr = self.as_array()
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x / length, sum_y / length

    def inside(self, bb: BoundingBox) -> bool:
        for p in self.vertices:
            if not p.inside(bb):
                return False
        return True

    def mostly_inside(self, bb: BoundingBox) -> bool:
        points_inside = 0
        points_outside = 0
        for p in self:
            if not p.inside(bb):
                points_outside += 1
            else:
                points_inside += 1
        return points_inside > points_outside

    def _parallel(self, p1: Position, p2: Position, offset_amount: float) -> Path:
        delta_y = p2.y - p1.y
        delta_x = p2.x - p1.x
        theta = math.atan2(delta_y, delta_x)

        line_a = Path()
        line_a.add(p1.x, p1.y)
        line_a.add(
            p1.x + offset_amount * math.cos(theta + math.pi / 2),
            p1.y + offset_amount * math.sin(theta + math.pi / 2),
        )

        line_b = Path()
        line_b.add(p2.x, p2.y)
        line_b.add(
            p2.x + offset_amount * math.cos(theta + math.pi / 2),
            p2.y + offset_amount * math.sin(theta + math.pi / 2),
        )

        out_path = Path()
        out_path.add(line_a[1].x, line_a[1].y)
        out_path.add(line_b[1].x, line_b[1].y)
        return out_path

    def _cross_product(self, a: list[float], b: list[float]) -> list[float]:
        return [a[1] * 0 - 0 * b[1], 0 * b[0] - a[0] * 0, a[0] * b[1] - a[1] * b[0]]

    def _extended_line(self, a: Position, b: Position, delta_a: float, delta_b: float) -> list[list[float]]:
        theta = math.atan2(b.y - a.y, b.x - a.x)
        new_a = [a.x - (delta_a * math.cos(theta)),
                 a.y - (delta_a * math.sin(theta))]
        new_b = [b.x + (delta_b * math.cos(theta)),
                 b.y + (delta_b * math.sin(theta))]

        return [new_a, new_b]

    def _offset_angle(
            self,
            p1: Position,
            p2: Position,
            p3: Position,
            offset: float,
    ) -> Path:
        a = p2.distance(p3)
        b = p1.distance(p2)
        c = p3.distance(p1)

        acos_arg = (math.pow(a, 2) + math.pow(b, 2) -
                    math.pow(c, 2)) / (2 * a * b)
        if abs(acos_arg) > 1:
            acos_arg = 0
        gamma = math.acos(acos_arg)
        corner_offset = offset * math.tan(math.pi / 2 - (0.5 * gamma))
        ac_offset = self._parallel(p1, p2, offset)
        vector_a = Position(p1.x - p2.x, p1.y - p2.y)
        vector_b = Position(p3.x - p2.x, p3.y - p2.y)
        cp = self._cross_product(vector_a.as_array(), vector_b.as_array())
        # cp = np.cross(vector_a.as_array(), vector_b.as_array())
        if cp[2] < 0:
            corner_offset = corner_offset * -1

        ac_offset = self._extended_line(
            ac_offset.vertices[0], ac_offset.vertices[1], 0, corner_offset
        )
        cb_offset = self._parallel(p2, p3, offset)

        out_path = Path()
        out_path.add(ac_offset[0][0], ac_offset[0][1])
        out_path.add(ac_offset[1][0], ac_offset[1][1])
        out_path.add(cb_offset[1].x, cb_offset[1].y)

        return out_path

    def offset(self, offset: float = 1.0) -> Path | None:
        """
        copied from https://github.com/markroland/path-helper/blob/main/src/PathHelper.js <3
        """
        if len(self) < 3:
            return None

        c = self.copy()
        offset_path = Path()

        for i in range(0, len(c) - 2, 1):
            j = i + 1
            k = i + 2
            offset_angle = self._offset_angle(
                c.vertices[i], c.vertices[j], c.vertices[k], -offset
            )
            if i == 0:
                offset_path.add(offset_angle[0].x, offset_angle[0].y)
                offset_path.add(offset_angle[1].x, offset_angle[1].y)
            elif i == len(c) - 3:
                offset_path.add(offset_angle[1].x, offset_angle[1].y)
                offset_path.add(offset_angle[2].x, offset_angle[2].y)
            else:
                offset_path.add(offset_angle[1].x, offset_angle[1].y)

        return offset_path

    def iter_and_return_path(self, offset: BaseGeometry) -> Path:
        pa = Path()
        for x, y in offset.coords:
            pa.add(x, y)
        return pa

    def add_if(self, pa: Path, out: list[Path]) -> None:
        if len(pa) > 2:
            pa.simplify(0.01)
            out.append(pa)

    def curve_offset(self, dist: float, join_style=JOIN_STYLE.mitre, mitre_limit: float = 1.0) -> list[Path]:
        return_paths = []

        line = LineString(self.as_tuple_list())
        result = line.offset_curve(dist, 16, join_style, mitre_limit)

        if type(result) is MultiLineString:
            for poi in result.geoms:
                pa = self.iter_and_return_path(poi)
                self.add_if(pa, return_paths)

        elif type(result) is LineString:
            pa = self.iter_and_return_path(result)
            self.add_if(pa, return_paths)

        return return_paths

    def parallel_offset(
            self, dist: float, join_style=JOIN_STYLE.mitre, mitre_limit: float = 1.0
    ) -> list[Path]:

        return_paths = []

        line = LineString(self.as_tuple_list())
        try:
            side = "right" if dist < 0 else "left"
            result = line.parallel_offset(
                abs(dist),
                side=side,
                resolution=256,
                join_style=join_style,
                mitre_limit=mitre_limit,
            )

            if type(result) is MultiLineString:
                for poi in result.geoms:
                    pa = self.iter_and_return_path(poi)
                    self.add_if(pa, return_paths)

            elif type(result) is LineString:
                pa = self.iter_and_return_path(result)
                self.add_if(pa, return_paths)

            else:
                print(f"nothing matched for type {type(result)}")
        except ValueError as ve:
            print(f"Exception {ve}")

        return return_paths

    def intersection_points(self, grid_size: float = 0.001) -> list[tuple[float, float]]:
        ls = LineString(self.as_tuple_list())
        # mls = unary_union(ls, 1)
        ls.normalize()
        mls = union_all(ls, grid_size)
        t = type(mls)
        linestring = None
        if t == shapely.geometry.multilinestring.MultiLineString:
            points = []
            for l in mls.geoms:
                for p in l.coords:
                    points.append(p)
            # linestring = mls.geoms[1]
            linestring = LineString(points)
        if t == shapely.geometry.linestring.LineString:
            linestring = mls

        # try:
        coords_list = []
        for non_itersecting_ls in linestring.coords:
            coords_list.append(non_itersecting_ls)
            # coords_list.extend(non_itersecting_ls.coords)

        return [
            item
            for item, count in collections.Counter(coords_list).items()
            if count > 1
        ]
        # except TypeError as te:
        #    log.warn("Couldnt calculate intersection points")
        #    log.warn(f"{te}")
        #    return []

    def smooth(self, size: int, shape: int) -> None:
        n = len(self)
        size = clamp(size, 0, n)
        shape = clamp(shape, 0, 1)

        weights = [0] * size
        for i in range(size):
            cur_weight = misc.map(i, 0, size, 1, shape, True)
            weights[i] = cur_weight

        result = self.copy()

        closed = False

        for i in range(n):
            sum = 1
            for j in range(1, size, 1):
                cur = Position()
                left_position = i - j
                right_position = i + j
                if left_position < 0 and closed:
                    left_position += n
                if left_position >= 0:
                    cur.translate(*self.vertices[left_position].as_tuple())
                    sum += weights[j]
                if right_position >= n and closed:
                    right_position -= n
                if right_position < n:
                    cur.translate(*self.vertices[right_position].as_tuple())
                    sum += weights[j]
                result.vertices[i].translate(
                    cur.x * weights[j], cur.y * weights[j])
            result.vertices[i].x = result.vertices[i].x / sum
            result.vertices[i].y = result.vertices[i].y / sum

        self.vertices = result.vertices

    def downsample(self, dist: float) -> None:
        prev = Position()
        self.vertices = [
            prev := v for v in self.vertices if v.distance(prev) > dist  # noqa: F841
        ]

    def resampled(self, target_dist: float) -> Path:
        # Calculate the cumulative distances along the line
        distances = [0.0]
        for i in range(1, len(self)):
            dx = self[i].x - self[i - 1].x
            dy = self[i].y - self[i - 1].y
            dist = np.sqrt(dx ** 2 + dy ** 2)
            distances.append(distances[-1] + dist)

        # Calculate number of intervals based on target_distance
        total_distance = distances[-1]
        num_intervals = int(total_distance / target_dist)

        # Determine the new distances for interpolation
        new_distances = [0.0] + \
            [i * target_dist for i in range(1, num_intervals + 1)]
        if new_distances[-1] > total_distance:
            new_distances.pop()

        # Use interpolation to get the new x and y coordinates
        new_x = np.interp(new_distances, distances, [p.x for p in self])
        new_y = np.interp(new_distances, distances, [p.y for p in self])

        new_vertices = list(zip(new_x, new_y))

        return Path.from_tuple_list(new_vertices)

    def resample(self, target_dist: float) -> None:
        self.vertices = self.resampled(target_dist).vertices

    def subset(self, start: int, end: int) -> Path:
        if start < 0 or start > len(self) or end < 0 or end > len(self):
            raise Exception("bounds should be within number of vertices")
        positions = self._vertices[start:end]
        pa = Path()
        for pos in positions:
            pa.add_position(pos)

        return pa

    def transform(self, bb: BoundingBox, out: BoundingBox) -> None:
        fn = misc.transformFn(
            (bb.x, bb.y), (bb.x2, bb.y2), (out.x, out.y), (out.x2, out.y2)
        )
        self.vertices = list(map(fn, self.vertices))

    def transformed(self, bb: BoundingBox, out: BoundingBox) -> Path:
        fn = misc.transformFn(
            (bb.x, bb.y), (bb.x2, bb.y2), (out.x, out.y), (out.x2, out.y2)
        )
        pa = Path()
        pa.properties = self.properties
        pa.vertices = list(map(fn, self.vertices))
        return pa

    def simplify(self, e: float = 1.0) -> None:
        # before = len(self.vertices)
        self.vertices = Path.from_tuple_list(
            ramer_douglas_peucker.rdp(self.as_tuple_list(), e)
        ).vertices
        # logging.info(f"Path::simplify({e}) reduced points {before} -> {len(self.vertices)}")

    @staticmethod
    def intersect_segment(p1: tuple[float, float],
                          p2: tuple[float, float],
                          p3: tuple[float, float],
                          p4: tuple[float, float]) -> tuple[float, float] | None:
        # https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0:  # parallel
            return None
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        if ua < 0 or ua > 1:  # out of range
            return None
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
        if ub < 0 or ub > 1:  # out of range
            return None
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return (x, y)

    def clip(self, bb: BoundingBox) -> list[Path] | None:
        any_inside = False
        for v in self.vertices:
            if v.inside(bb):
                any_inside = True
                break

        if not any_inside:
            return

        def get_intersection(
                segment: Path, paths: list[tuple[float, float, float, float]]
        ) -> tuple[float, float]:
            for p in paths:
                tup1 = segment[0].as_tuple()
                tup2 = segment[1].as_tuple()
                intersect = Path.intersect_segment(
                    (p[0], p[1]), (p[2], p[3]), tup1, tup2
                )
                if intersect is not None:
                    return intersect[0], intersect[1]
            raise Exception("no intersection with anything")

        bb_lines = bb.paths()
        prev_v = None
        new_paths = []
        current_path = Path()
        for v in self.vertices:
            if prev_v is not None:
                prev_inside = prev_v.inside(bb)
                curr_inside = v.inside(bb)
                if prev_inside and curr_inside:
                    current_path.add_position(v)
                if prev_inside and not curr_inside:
                    p = Path()
                    p.add(prev_v.x, prev_v.y)
                    p.add(v.x, v.y)
                    intersection = get_intersection(p, bb_lines)
                    current_path.add_position(
                        Position(intersection[0], intersection[1])
                    )
                    new_paths.append(current_path.copy())
                    current_path = Path()
                if not prev_inside and curr_inside:
                    p = Path()
                    p.add(prev_v.x, prev_v.y)
                    p.add(v.x, v.y)
                    intersection = get_intersection(p, bb_lines)
                    current_path.add_position(
                        Position(intersection[0], intersection[1])
                    )
                    current_path.add_position(Position(v.x, v.y))
            else:
                if v.inside(bb):
                    current_path.add_position(v)
            prev_v = v
        if not current_path.empty():
            new_paths.append(current_path)
        return new_paths

    def split_by_color(self) -> list[Path]:
        paths_list = []
        current = Path()
        current.add_position(self.vertices[0])
        for v in self.vertices[1:]:
            if current[-1].color == v.color:
                current.add_position(v)
            else:
                pos = Position(v.x, v.y, v.timestamp)
                pos.color = current[-1].color
                current.add_position(pos)
                paths_list.append(current)
                current = Path()
                current.add_position(v)

        current.add_position(self.vertices[-1])
        paths_list.append(current)
        return paths_list

    def clip_shapely(self, bb: BoundingBox) -> list[Path]:
        def iter_and_return_path(offset: BaseGeometry) -> Path:
            pa = Path()
            for x, y in offset.coords:
                pa.add(x, y)
            return pa

        def add_if(pa: Path, out: list[Path]):
            # if len(pa) > 2:
            # pa.simplify(0.01)
            out.append(pa)

        line = LineString(self.as_tuple_list())
        result = clip_by_rect(line, bb.x, bb.y, bb.x2, bb.y2)

        return_paths = []

        if type(result) is MultiLineString:
            for poi in result.geoms:
                pa = iter_and_return_path(poi)
                add_if(pa, return_paths)

        elif type(result) is LineString:
            pa = iter_and_return_path(result)
            add_if(pa, return_paths)

        # we've been copying stuff before, this
        # would have been lost
        for pa in return_paths:
            pa.properties = self.properties

        return return_paths

    def is_1_dimensional(self) -> bool:
        """
        returns whether all x or y coordinates are the same
        """

        tuple_list = self.as_tuple_list()
        x_values, y_values = zip(*tuple_list)

        return len(set(x_values)) == 1 or len(set(y_values)) == 1

    @timing
    def vertical_line_test(self, res: float = 0.1) -> tuple[bool, list[list[Position]]]:
        f_direction_vector = self.end_pos() - self.start_pos()
        f_perp_vector = Position(-f_direction_vector.y, f_direction_vector.x)

        # normalize perpendicular direction vector
        mag = math.sqrt((f_perp_vector.x * f_perp_vector.x) +
                        (f_perp_vector.y * f_perp_vector.y))
        ray_dir = Position(f_perp_vector.x / mag, f_perp_vector.y / mag)

        perc = 0.0
        all_intersections = []
        while perc <= 1.0:
            """
            This is iterating via slices through a line
            percentage is the slice between [0, 1]
            """
            lerped_x = misc.lerp(self.start_pos().x, self.end_pos().x, perc)
            lerped_y = misc.lerp(self.start_pos().y, self.end_pos().y, perc)
            ray_origin = Position(lerped_x, lerped_y)

            intersections: set[Position] = set()

            # iterate through all paths, check for intersections at current slice
            for p in range(len(self) - 1):
                start = self[p]
                end = self[p + 1]

                intersection = line_intersection(
                    ray_origin.as_array(), ray_dir.as_array(),
                    start.as_array(), end.as_array())

                if intersection:
                    intersections.add(Position.from_array(intersection))

            perc += res
            all_intersections.append(list(intersections))

        # if any of the lists within this returned list have a length > 1
        # means there were two intersections with the slice and the path is not functional

        is_functional = not any(len(e) > 1 for e in all_intersections)
        return is_functional, all_intersections

    def vertical_line_test2(self, n_sample_points: int | None = None) -> tuple[bool, list[set[Position]]]:
        """
        the previous implementation has the bug that it doesnt detect a curved path
        new idea: take n random points on the path instead of lerped x,y pos at an interval
        """

        if not n_sample_points:
            n_sample_points = len(self)

        # no need to over-sample
        if len(self) < n_sample_points:
            n_sample_points = len(self)

        f_direction_vector = self.end_pos() - self.start_pos()
        f_perp_vector = Position(-f_direction_vector.y, f_direction_vector.x)

        # normalize perpendicular direction vector
        mag = math.sqrt((f_perp_vector.x * f_perp_vector.x) +
                        (f_perp_vector.y * f_perp_vector.y))
        ray_dir = Position(f_perp_vector.x / mag, f_perp_vector.y / mag)

        all_intersections = []
        # logging.info(f"sample_points: {n_sample_points}")
        for i in range(n_sample_points):
            """
            This is iterating via slices through a line
            percentage is the slice between [0, 1]
            """
            idx = int(misc.map(i, 0, n_sample_points, 0, len(self)))
            ray_origin = self[idx]

            intersections = set()

            # iterate through all paths, check for intersections at current slice
            for p in range(len(self) - 1):
                start = self[p]
                end = self[p + 1]

                intersection = line_intersection(
                    ray_origin.as_array(), ray_dir.as_array(),
                    start.as_array(), end.as_array())

                if intersection:
                    intersections.add(Position.from_array(intersection))

            all_intersections.append(intersections)

        # if any of the lists within this returned list have a length > 1
        # means there were two intersections with the slice and the path is not functional

        is_functional = not any(len(e) > 1 for e in all_intersections)
        return is_functional, all_intersections

    def vertical_line_test_fast(self) -> bool:
        morped_path = self.morph((0, 0), (1, 0))
        for i in range(len(morped_path) - 1):
            _from = morped_path[i]
            _to = morped_path[i + 1]

            if _to.x <= _from.x:
                return False

        return True

    def rotated_into_bb(self, target_bb: BoundingBox) -> Path:
        if self.is_1_dimensional():
            logging.warn("Didn't rotate, bc path is 1-dimensional.")
            return self

        line = LineString(self.as_tuple_list())
        rect = line.minimum_rotated_rectangle

        target_poly = Polygon(
            [
                [0, 0],
                [target_bb.x2, 0],
                [target_bb.x2, target_bb.y2],
                [0, target_bb.y2],
                [0, 0],
            ]
        )

        src = np.array(rect.exterior.coords)
        dst = np.array(target_poly.exterior.coords)
        matrix = estimate_transform("similarity", src, dst).params
        matrix = np.append(matrix, [[0, 0, 0]], axis=0).flatten()

        tuple_list = apply_matrix(self.as_tuple_list(), matrix)

        pa = Path()
        for tup in tuple_list:
            pa.add_position(Position.from_tuple(tup))

        # somehow the matrix application above doesnt scale well
        pa.transform(pa.bb(), target_bb)
        return pa

    def rotate_into_bb(self, target_bb: BoundingBox) -> None:
        _rotated = self.rotated_into_bb(target_bb)
        self.vertices = _rotated.vertices
