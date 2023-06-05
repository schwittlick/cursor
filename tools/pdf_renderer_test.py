from fpdf import fpdf

from cursor.data import DataDirHandler
from cursor.device import Paper, PaperSize
from cursor.loader import Loader
from cursor.renderer import JpegRenderer, AsciiRenderer

if __name__ == "__main__":
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.PORTRAIT_A4],
        padding_mm=0,
        cutoff_mm=0,
    )

    r = JpegRenderer(DataDirHandler().test_images())
    a = AsciiRenderer(DataDirHandler().test_ascii(), r)
    a.render(rec, scale=1, thickness=30)

    text = a.output.splitlines()

    pdf = fpdf.FPDF(orientation="L", unit="mm", format="A4")

    fontpath = DataDirHandler().test_data_file("JetBrainsMono-Regular.ttf")
    pdf.add_font(
        "JetbrainsMono",
        "",
        fontpath.as_posix(),
        uni=True,
    )
    pdf.add_page()
    pdf.set_margins(0, 0)
    pdf.set_font("JetbrainsMono", size=14)
    linecounter = 0
    for line in text:
        # pdf.cell(0, 3, txt=line, ln=1, align="L")
        pdf.text(0, linecounter * 6 + 5, line)
        linecounter += 1

    out = DataDirHandler().test_data_dir / "simple_demo.pdf"
    pdf.output(out)
