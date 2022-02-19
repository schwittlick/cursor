from cursor.path import Path, Spiral, PathCollection
from cursor import device
from cursor import renderer
from cursor import data
from cursor import filter


if __name__ == "__main__":
    name = "c59_pptx_video"
    images_folder = data.DataDirHandler().video(name)
    video = renderer.VideoRenderer(images_folder)
    offs = 1
    for frame in range(200):
        jpeg_renderer = renderer.JpegRenderer(images_folder)
        coll = PathCollection()
        print(f"frame {frame}")
        for i in range(16):
            x = i % 4
            y = (i - x) / 4
            inside = "test"
            pp = Path(layer=f"{inside}")
            spiral = Spiral()
            spiral.max_theta = 255
            spiral.xoffset_incr = offs
            p = spiral.custom(pp)
            p.translate(x * 2250, y * 250)
            coll.add(p)
            offs -= 0.001

        coll.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1])
        f = filter.DistanceBetweenPointsFilter(1.25)
        f.filter(coll)
        r = renderer.RealtimeRenderer()
        r.render(coll)
        jpeg_renderer.render(coll)
        jpeg_renderer.save(f"out_{frame:05d}")

    video.render_video("c59_pptx.mp4")
