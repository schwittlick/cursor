import logging

from cursor.data import DateHandler
from cursor.path import Path
from cursor.renderer.realtime import RealtimeRenderer


def print_path_info(path: Path) -> None:
    logging.info(f"Path: {path}")
    logging.info(f"Entropy x={path.entropy_x:.4} y={path.entropy_y:.4}")
    logging.info(f"Entropy differential x={path.differential_entropy_x:.4} y={path.differential_entropy_y:.4}")
    logging.info(f"Variation x={path.variation_x:.4} y={path.variation_y:.4}")
    logging.info(f"Entropy direction change= {path.entropy_direction_changes:.4}")
    logging.info(f"Duration {path.duration}s")
    logging.info(f"Length/Distance {path.distance}")
    logging.info(f"Area {path.bb().area()}")
    logging.info(f"Aspect ratio {path.aspect_ratio()}")


class RecorderTool(RealtimeRenderer):
    def __init__(self):
        super().__init__(600, 600, "recorder_tool")

        self.path = Path()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        # adding positions normalized
        self.path.add(x / self.width, y / self.height, int(DateHandler.utc_timestamp()))

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        # printing information of normalized path
        print_path_info(self.path)

        # scaled for rendering
        scaled = self.path.scaled(self.width, self.height)
        self.add_path(scaled)

        # clear for next path
        self.path.clear()


if __name__ == "__main__":
    RecorderTool().run()
