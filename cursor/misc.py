from cursor import data
from cursor import renderer


def save_wrapper(pc, projname, fname):
    jpeg_folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(jpeg_folder)

    jpeg_renderer.render(pc, scale=1.0)
    jpeg_renderer.save(fname)

    svg_folder = data.DataDirHandler().svg(projname)
    svg_renderer = renderer.SvgRenderer(svg_folder)

    svg_renderer.render(pc)
    svg_renderer.save(fname)


def save_wrapper_jpeg(pc, projname, fname, scale=4.0, thickness=3):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=scale, thickness=thickness)
    jpeg_renderer.save(fname)
