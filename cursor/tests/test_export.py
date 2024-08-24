import pytest
from unittest.mock import Mock, patch

from cursor.algorithm.color.copic import Color
from cursor.collection import Collection
from cursor.path import Path as CursorPath
from cursor.device import PlotterType
from cursor.export import ExportWrapper, Exporter, ExportConfig


@pytest.fixture
def sample_collection():
    p1 = CursorPath()
    p1.add(3, 5)
    p1.add(5, 9)
    p1.add(3, 10)
    p1.pen_select = 1

    p2 = CursorPath()
    p2.add(1, 6)
    p2.add(3, 5)
    p2.add(3, 8)
    p2.pen_select = 2

    pc = Collection()
    pc.add(p1)
    pc.add(p2)
    return pc


@pytest.fixture
def export_wrapper(sample_collection):
    return ExportWrapper(
        sample_collection,
        PlotterType.HP_7470A_A4,
        25,
        "test",
        "111",
        keep_aspect_ratio=False,
    )


def test_export_wrapper_initialization(export_wrapper):
    assert export_wrapper.paths is not None
    assert export_wrapper.ptype == PlotterType.HP_7470A_A4
    assert export_wrapper.margin == 25
    assert export_wrapper.name == "test"
    assert export_wrapper.suffix == "111"
    assert export_wrapper.keep_aspect_ratio is False


def test_export_wrapper_fit(export_wrapper):
    with patch.object(Exporter, "fit") as mock_fit:
        export_wrapper.fit()
        mock_fit.assert_called_once()


def test_export_wrapper_ex(export_wrapper):
    with patch.object(Exporter, "run") as mock_run:
        export_wrapper.ex()
        mock_run.assert_called_once()


def test_export_wrapper_ex_reversed(export_wrapper):
    export_wrapper.export_reversed = True
    with patch.object(Exporter, "run") as mock_run, patch.object(
        Collection, "reverse"
    ) as mock_reverse:
        export_wrapper.ex()
        assert mock_run.call_count == 2
        mock_reverse.assert_called_once()


@pytest.fixture
def exporter(sample_collection):
    exp = Exporter(sample_collection)
    exp.cfg = ExportConfig(PlotterType.HP_7470A_A4, 25, None, False, False, True)
    exp.name = "test"
    exp.suffix = "111"
    exp.gcode_speed = None
    exp.keep_aspect_ratio = False
    return exp


def test_exporter_initialization(exporter):
    assert exporter.collection is not None
    assert exporter.cfg is not None
    assert exporter.name == "test"
    assert exporter.suffix == "111"
    assert exporter.gcode_speed is None
    assert exporter.keep_aspect_ratio is False


def test_exporter_fit(exporter):
    with patch.object(Collection, "fit") as mock_fit:
        exporter.fit()
        mock_fit.assert_called_once()


def test_exporter_print_pen_move_distances(exporter, caplog):
    exporter.print_pen_move_distances(exporter.collection)
    assert "Total pen-down distance:" in caplog.text
    assert "Total pen-up distance:" in caplog.text


@pytest.mark.parametrize(
    "format_type, export_method",
    [
        (PlotterType.HP_7470A_A4, "_export_hpgl"),
        (PlotterType.ROLAND_DXY990, "_export_hpgl"),
        (PlotterType.AXIDRAW, "_export_svg"),
        (PlotterType.DIY_PLOTTER, "_export_gcode"),
        (PlotterType.TEKTRONIX_4662, "_export_tek"),
        (PlotterType.DIGIPLOT_A1, "_export_digi"),
    ],
)
def test_exporter_run(exporter, format_type, export_method):
    exporter.cfg.type = format_type
    with patch.object(Exporter, export_method) as mock_export:
        exporter.run()
        mock_export.assert_called()


def test_exporter_generate_filename(exporter):
    filename = exporter._generate_filename("layer1")
    assert exporter.name in filename
    assert exporter.suffix in filename
    assert "layer1" in filename


def test_export_jpeg_preview(exporter):
    with patch("cursor.export.JpegRenderer") as mock_jpeg_renderer:
        exporter.export_jpeg_preview({"layer1": exporter.collection})
        mock_jpeg_renderer.assert_called_once()


def test_export_source(exporter, tmp_path):
    with patch("cursor.export.DataDirHandler") as mock_data_dir_handler:
        mock_data_dir_handler().source.return_value = tmp_path
        exporter.export_source()
        assert len(list(tmp_path.glob("*.py"))) == 1


def test_export_copic_color_mapping(exporter):
    exporter.collection.properties["pen_mapping"] = {"layer1": {1: "R27", 2: "B29"}}
    with patch("cursor.export.PdfRenderer") as mock_pdf_renderer, patch(
        "cursor.export.Copic"
    ) as mock_copic:
        mock_color = Mock(spec=Color)
        mock_color.as_rgb.return_value = (255, 0, 0)
        mock_copic.return_value.color_by_code.return_value = mock_color
        exporter.export_copic_color_mapping("test", {"layer1": exporter.collection})
    mock_pdf_renderer.assert_called_once()
    mock_copic.return_value.color_by_code.assert_called()


if __name__ == "__main__":
    pytest.main()
