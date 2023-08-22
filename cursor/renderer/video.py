from __future__ import annotations

import os
import pathlib


class VideoRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path = folder
        self.images = []

    def add_frame(self, img) -> None:
        self.images.append(img)

    def render_video(self, fname: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        text_file = (self.save_path / "list.txt").as_posix()

        p = pathlib.Path(self.save_path.absolute()).glob("**/*.jpg")
        files = [x for x in p if x.is_file()]
        with open(text_file, "w", encoding="utf8") as file:
            for f in files:
                file.write("file '")
                file.write(f.as_posix().replace("/", "\\"))
                file.write("'")
                file.write("\n")

        out_file = self.save_path / fname
        call = (
            f'ffmpeg -y -r 25 -f concat -safe 0 -i "{text_file}" -c:v libx264 -vf '
            f'"fps=25,format=yuv420p,scale=trunc(iw/2)*2:trunc(ih/2)*2" {out_file}'
        )

        os.system(call)
