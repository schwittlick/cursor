from __future__ import annotations

import pathlib
import logging

from cursor.collection import Collection


class GCodeRenderer:
    def __init__(
            self,
            folder: pathlib.Path,
            feedrate_xy: int = 2000,
            feedrate_z: int = 1000,
            z_down: float = 3.5,
            z_up: float = 0.0,
            invert_y: bool = False,
    ):
        self.save_path = folder
        self.z_down = z_down
        self.z_up = z_up
        self.feedrate_xy = feedrate_xy
        self.feedrate_z = feedrate_z
        self.invert_y = invert_y
        self.paths = Collection()

    def render(self, paths: Collection) -> None:
        logging.info(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def g01(self, x: float, y: float, z: float) -> str:
        return f"G01 X{x:.2f} Y{y:.2f} Z{z:.2f} F{self.feedrate_xy}"

    def generate_instructions(self) -> list[str]:
        instructions = []
        instructions.append(self.g01(0, 0, self.z_up))
        for p in self.paths:
            x = p.start_pos().x
            y = p.start_pos().y
            z = self.z_down
            if self.invert_y:
                y = -y

            if "skip_up" not in p.properties.keys():
                # dont skip pen up move if property was set
                instructions.append(self.g01(x, y, self.z_up))

            if "z" in self.paths[0].properties:
                z = self.paths[0].properties["z"]

            # instructions.append(self.g01(x, y, z))

            if "laser" in p.properties:
                instructions.append("LASERON")
            if "amp" in p.properties.keys():
                amp = p.properties["amp"]
                instructions.append(f"AMP{amp:.3}")
            if "volt" in p.properties.keys():
                volt = p.properties["volt"]
                instructions.append(f"VOLT{volt:.3}")

            for point in p.vertices:
                x = point.x
                y = point.y
                if self.invert_y:
                    y = -y
                z = self.z_down

                if "z" in point.properties.keys():
                    z = point.properties["z"]

                if "amp" in point.properties.keys():
                    amp = point.properties["amp"]
                    instructions.append(f"AMP{amp:.3}")
                if "volt" in point.properties.keys():
                    volt = point.properties["volt"]
                    instructions.append(f"VOLT{volt:.3}")

                instructions.append(self.g01(x, y, z))

                if "laser" in point.properties.keys():
                    instructions.append("LASERON")

                if "delay" in point.properties.keys():
                    delay = point.properties["delay"]
                    instructions.append(f"DELAY{delay:.2}")

                if "laser" in point.properties.keys():
                    instructions.append("LASEROFF")

            if p.laser_onoff:
                instructions.append("LASEROFF")

            if "skip_up" in p.properties.keys():
                # skip pen up move if property was set
                continue
            instructions.append(self.g01(x, y, self.z_up))
        instructions.append(self.g01(0, 0, self.z_up))

        return instructions

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
        fname = self.save_path / (filename + ".nc")
        instructions = self.generate_instructions()

        with open(fname.as_posix(), "w") as file:
            for instruction in instructions:
                file.write(f"{instruction}\n")
        logging.info(f"Finished saving {fname}")
