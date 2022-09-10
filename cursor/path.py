from cursor.misc import dot_product
from cursor.misc import length
from cursor.misc import determinant
from cursor.misc import mix
from cursor.misc import entropy2
from cursor.misc import map
from cursor.misc import euclidean
from cursor.misc import LinearDiscreteFrechet

from cursor.position import Position
from cursor.bb import BoundingBox

import numpy as np
import math
import hashlib
import wasabi
import copy
import typing
from scipy import spatial


log = wasabi.Printer()


class Path:
    def __init__(
        self,
        vertices: typing.Optional[list] = None,
        layer: typing.Optional[str] = "layer1",
        line_type: typing.Optional[int] = None,
        pen_velocity: typing.Optional[int] = None,
        pen_force: typing.Optional[int] = None,
        pen_select: typing.Optional[int] = None,
        is_polygon: typing.Optional[bool] = False,
    ):
        self._layer = layer
        self._line_type = line_type
        self._pen_velocity = pen_velocity
        self._pen_force = pen_force
        self._pen_select = pen_select
        self._is_polygon = is_polygon
        if vertices:
            self._vertices = list(vertices)
        else:
            self._vertices = []

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self.vertices).encode("utf-8")).hexdigest()

    @property
    def vertices(self) -> typing.List[Position]:
        return self._vertices

    @vertices.setter
    def vertices(self, vertices: typing.List[Position]) -> None:
        self._vertices = vertices

    @property
    def line_type(self) -> int:
        """
        only linetype of 1 and above allowed
        all other linetypes don't render well
        """
        if self._line_type is None:
            return 1
        return max(self._line_type, 1)

    @line_type.setter
    def line_type(self, line_type) -> None:
        if line_type <= 0:
            self._line_type = 1
        self._line_type = line_type

    @property
    def layer(self) -> int:
        return self._layer

    @layer.setter
    def layer(self, layer) -> None:
        self._layer = layer

    @property
    def pen_force(self) -> int:
        return self._pen_force

    @pen_force.setter
    def pen_force(self, pen_force) -> None:
        self._pen_force = pen_force

    @property
    def pen_select(self) -> int:
        return self._pen_select

    @pen_select.setter
    def pen_select(self, pen_select) -> None:
        self._pen_select = pen_select

    @property
    def velocity(self) -> int:
        return self._pen_velocity

    @velocity.setter
    def velocity(self, pen_velocity) -> None:
        self._pen_velocity = pen_velocity

    @property
    def is_polygon(self) -> bool:
        return self._is_polygon

    @is_polygon.setter
    def is_polygon(self, is_polygon) -> None:
        self._is_polygon = is_polygon

    def add(self, x: float, y: float, timestamp: int = 0) -> None:
        self.vertices.append(Position(x, y, timestamp))

    def add_position(self, pos: Position) -> None:
        self.vertices.append(pos)

    def arr(self) -> np.array:
        data = []
        idx = 0
        for p in self.vertices:
            data.append(p.arr())

            idx += 1
        arr = np.array(data)
        return arr

    def clear(self) -> None:
        self.vertices.clear()

    def copy(self) -> "Path":
        p = type(self)(copy.deepcopy(self.vertices))
        p.layer = self.layer
        p.velocity = self.velocity
        p.line_type = self.line_type
        p.pen_select = self.pen_select
        p.pen_force = self.pen_force
        p.is_polygon = self.is_polygon
        return p

    def reverse(self) -> None:
        self.vertices.reverse()

    def reversed(self) -> "Path":
        c = copy.deepcopy(self.vertices)
        c.reverse()
        return Path(
            c, layer=self.layer, line_type=self.line_type, pen_velocity=self.velocity
        )

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

    def aspect_ratio(self) -> float:
        if len(self) < 2:
            return math.nan

        _bb = self.bb()
        if _bb.w == 0.0 or _bb.h == 0.0:
            return math.nan

        return _bb.h / _bb.w

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

        for i in range(self.__len__() - 1):
            current = self.__getitem__(i)
            next = self.__getitem__(i + 1)

            d = calculateDistance(current.x, current.y, next.x, next.y)
            dist += d

        return dist

    def translate(self, x: float, y: float) -> None:
        for p in self.vertices:
            p.translate(x, y)

    def scale(self, x: float, y: float) -> None:
        for p in self.vertices:
            p.scale(x, y)

    def rot(
        self, angle: float, origin: typing.Tuple[float, float] = (0.0, 0.0)
    ) -> None:
        for p in self.vertices:
            p.rot(angle, origin)

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

    def fit(self, bb: BoundingBox) -> None:
        pass

    def morph(
        self,
        start: typing.Union["Position", typing.Tuple[float, float]],
        end: typing.Union["Position", typing.Tuple[float, float]],
    ) -> "Path":
        if isinstance(start, Position) and isinstance(end, Position):
            start = (start.x, start.y)
            end = (end.x, end.y)

        path = Path()
        end_np = self.end_pos().arr()
        start_np = self.start_pos().arr()
        new_end_np = np.array(end, dtype=float)
        new_start_np = np.array(start, dtype=float)

        for point in self.vertices:
            nparr = point.arr()

            dir_old = np.subtract(end_np, start_np)
            dir_new = np.subtract(new_end_np, new_start_np)
            mag_diff = np.linalg.norm(dir_new) / np.linalg.norm(dir_old)
            if mag_diff is np.nan:
                mag_diff = 0.0
            if math.isinf(mag_diff):
                mag_diff = 1.0
            nparr = nparr * mag_diff
            path.add(nparr[0], nparr[1], point.timestamp)

        current_end = path.end_pos().arr()
        current_start = path.start_pos().arr()
        current_start_to_end = np.subtract(current_end, current_start)

        new_start_to_end = np.subtract(new_end_np, new_start_np)

        current_start_to_end = current_start_to_end / np.linalg.norm(
            current_start_to_end
        )
        new_start_to_end = new_start_to_end / np.linalg.norm(new_start_to_end)

        try:
            angle = np.arccos(
                np.clip(
                    np.dot(current_start_to_end, new_start_to_end), -math.pi, math.pi
                )
            )
        except RuntimeWarning as w:
            log.fail(w)

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

        translation = np.subtract(new_start_np, path.start_pos().arr())
        for p in path.vertices:
            p.translate(translation[0], translation[1])

        return path

    def intersect(self, newpath: "Path") -> typing.Tuple[bool, float, float]:
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
                    intersectionx = (
                        -((diffLAx * compareB) - (compareA * diffLBx)) * lDetDivInv
                    )
                    intersectiony = (
                        -((diffLAy * compareB) - (compareA * diffLBy)) * lDetDivInv
                    )

                    return True, intersectionx, intersectiony

        return False, 0.0, 0.0

    def interp(self, newpath: "Path", perc: float) -> "Path":
        path = Path()

        maxpoint = max(len(newpath), len(self))

        for i in range(maxpoint):
            idxthis = int((float(i) / maxpoint) * len(self))
            idxnew = int((float(i) / maxpoint) * len(newpath))

            pthis = self[idxthis]
            pnew = newpath[idxnew]
            x_interp = mix(pthis.x, pnew.x, perc)
            y_interp = mix(pthis.y, pnew.y, perc)
            time_interp = mix(pthis.timestamp, pnew.timestamp, perc)

            path.add(x_interp, y_interp, int(time_interp))

        return path

    def direction_changes_pos_neg(self) -> typing.List[float]:
        """
        returns a list of radial direction changes from each point
        to the next len() = self.__len() - 1
        :return:
        """

        angles = []
        idx = 0
        prev = 0
        for _ in self.vertices:
            if idx > 0:
                f = self.vertices[idx - 1]
                s = self.vertices[idx]

                ang = math.atan2(s.y - f.y, s.x - f.x)
                ang = math.degrees(ang)

                angles.append(ang - prev)
                prev = ang
            idx += 1

        return angles

    def inner_angle(self, v: tuple[float, float], w: tuple[float, float]):
        dp = dot_product(v, w)
        ll = length(v) * length(w)
        if ll == 0.0:
            return 0.0

        cosx = dp / ll

        if cosx < -1.0:
            cosx = -1.0
        if cosx > 1.0:
            cosx = 1.0

        rad = np.arccos(cosx)  # in radians
        deg1 = math.degrees(rad)
        return deg1  # returns degrees

    def angle_clockwise(self, A, B):
        inner = self.inner_angle(A, B)
        det = determinant(A, B)
        if det < 0:
            # this is a property of the det. If the det < 0 then B is clockwise of A
            return inner
        else:  # if the det > 0 then A is immediately clockwise of B
            return 360 - inner

    def direction_changes(self) -> typing.List[float]:
        """
        returns a list of radial direction changes from each point
        to the next len() = self.__len() - 1
        :return:
        """
        angles = []
        idx = 0
        for _ in self.vertices:
            if idx > 0:
                f = self.vertices[idx - 1]
                s = self.vertices[idx]
                angle = self.angle_clockwise(f.astuple(), s.astuple())
                # angle = angle_clockwise((1, 1), (1, -1))

                if angle > 180:
                    angle = 360 - angle

                # angles.append(np.deg2rad(angle) % (2 * np.pi))
                angles.append(angle % 360)
            idx += 1

        return angles

    @property
    def shannon_x(self) -> float:
        distances = []

        first = True
        prevx = None
        for v in self.vertices:
            if first:
                prevx = v.x
                first = False
                continue

            dist = v.x - prevx
            distances.append(dist)

            prevx = v.x

        entropy = entropy2(distances)
        return entropy

    @property
    def shannon_y(self) -> float:
        distances = []

        first = True
        prevy = None
        for v in self.vertices:
            if first:
                prevy = v.y
                first = False
                continue

            dist = v.y - prevy
            distances.append(dist)

            prevy = v.y

        entropy = entropy2(distances)
        return entropy

    @property
    def shannon_direction_changes(self) -> float:
        entropy = entropy2(self.direction_changes())
        if entropy is np.nan:
            log.fail("LOL")
        return entropy

    def empty(self) -> bool:
        return len(self.vertices) < 1

    def clean(self) -> None:
        """
        removes consecutive duplicates
        """

        prev = Position()
        self.vertices = [prev := v for v in self.vertices if prev != v]  # noqa: F841

    def limit(self) -> None:
        """
        removes points larger than 1.0
        """
        self.vertices = [
            v for v in self.vertices if 1.0 >= v.x >= 0.0 and 1.0 >= v.y >= 0.0
        ]

    def similarity(self, _path: "Path") -> float:
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

    def frechet_similarity(self, _path: "Path") -> float:
        """
        https://github.com/joaofig/discrete-frechet
        """
        distance = euclidean
        fdfs = LinearDiscreteFrechet(distance)
        return fdfs.distance(self.arr(), _path.arr())

    def centeroid(self) -> typing.Tuple[float, float]:
        arr = self.arr()
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x / length, sum_y / length

    def inside(self, bb: BoundingBox) -> bool:
        for p in self:
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

    def _parallel(self, p1: "Position", p2: "Position", offset_amount: float):
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

    def _cross_product(self, a, b):
        return [a[1] * 0 - 0 * b[1], 0 * b[0] - a[0] * 0, a[0] * b[1] - a[1] * b[0]]

    def _extended_line(self, a, b, delta_a, delta_b):
        theta = math.atan2(b.y - a.y, b.x - a.x)
        new_a = [a.x - (delta_a * math.cos(theta)), a.y - (delta_a * math.sin(theta))]
        new_b = [b.x + (delta_b * math.cos(theta)), b.y + (delta_b * math.sin(theta))]

        return [new_a, new_b]

    def _offset_angle(
        self,
        p1: "Position",
        p2: "Position",
        p3: "Position",
        offset: float,
    ) -> "Path":
        a = p2.distance(p3)
        b = p1.distance(p2)
        c = p3.distance(p1)

        acos_arg = (math.pow(a, 2) + math.pow(b, 2) - math.pow(c, 2)) / (2 * a * b)
        if abs(acos_arg) > 1:
            acos_arg = 0
        gamma = math.acos(acos_arg)
        corner_offset = offset * math.tan(math.pi / 2 - (0.5 * gamma))
        ac_offset = self._parallel(p1, p2, offset)
        vector_a = Position(p1.x - p2.x, p1.y - p2.y)
        vector_b = Position(p3.x - p2.x, p3.y - p2.y)
        cp = self._cross_product(
            vector_a.arr(), vector_b.arr()
        )  # np.cross(vector_a.arr(), vector_b.arr())
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

    def offset(self, offset: float = 1.0) -> typing.Optional["Path"]:
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

    def parallel_offset(self):
        # from shapely.geometry import LineString

        """
        same as above but via shapely lib
        """
        pass

    @staticmethod
    def clamp(n, smallest, largest):
        return max(smallest, min(n, largest))

    def smooth(self, size: int, shape: int) -> None:
        n = len(self)
        size = Path.clamp(size, 0, n)
        shape = Path.clamp(shape, 0, 1)

        weights = [0] * size
        for i in range(size):
            cur_weight = map(i, 0, size, 1, shape, True)
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
                    cur.translate(*self.vertices[left_position].astuple())
                    sum += weights[j]
                if right_position >= n and closed:
                    right_position -= n
                if right_position < n:
                    cur.translate(*self.vertices[right_position].astuple())
                    sum += weights[j]
                result.vertices[i].translate(cur.x * weights[j], cur.y * weights[j])
            result.vertices[i].x = result.vertices[i].x / sum
            result.vertices[i].y = result.vertices[i].y / sum

        self.vertices = result.vertices

    def downsample(self, dist: float) -> None:
        prev = Position()
        self.vertices = [
            prev := v for v in self.vertices if v.distance(prev) > dist  # noqa: F841
        ]

    @staticmethod
    def intersect_segment(p1, p2, p3, p4):
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

    def clip(self, bb: BoundingBox) -> typing.Optional[typing.List["Path"]]:
        any_inside = False
        for v in self.vertices:
            if v.inside(bb):
                any_inside = True
                break

        if not any_inside:
            return

        def get_intersection(
            segment: Path, paths: typing.List[typing.Tuple[float, float, float, float]]
        ) -> typing.Tuple[float, float]:
            for p in paths:
                tup1 = segment[0].astuple()
                tup2 = segment[1].astuple()
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

    def __repr__(self):
        rep = (
            f"verts: {len(self.vertices)} shannx: {self.shannon_x} shanny: {self.shannon_y} "
            f"shannchan: {self.shannon_direction_changes} layer: {self.layer} "
            f"type: {self.line_type} velocity: {self.velocity} "
            f"bb: {self.bb()}"
        )
        return rep

    def __len__(self) -> int:
        return len(self.vertices)

    def __iter__(self) -> typing.Iterator["Path"]:
        for v in self.vertices:
            yield v

    def __getitem__(self, item) -> Position:
        return self.vertices[item].copy()
