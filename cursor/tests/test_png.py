import pytest
import pathlib
import cairo
from unittest.mock import patch, MagicMock

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property
from cursor.renderer.png import CairoRenderer


@pytest.fixture
def renderer():
    test_folder = pathlib.Path("/tmp/test_cairo_renderer")
    return CairoRenderer(test_folder)


def test_init(renderer):
    assert isinstance(renderer.surface, cairo.ImageSurface)
    assert isinstance(renderer.ctx, cairo.Context)
    assert renderer.surface.get_width() == 1920
    assert renderer.surface.get_height() == 1080
    assert isinstance(renderer.collection, Collection)
    assert isinstance(renderer.positions, list)


def test_background(renderer):
    renderer.background((255, 0, 0))
    assert renderer._background == (255, 0, 0)


def test_render(renderer):
    with patch.object(CairoRenderer, 'render_all_paths') as mock_paths, \
            patch.object(CairoRenderer, 'render_all_points') as mock_points, \
            patch.object(CairoRenderer, 'render_frame') as mock_frame:
        renderer.render(scale=2.0, frame=True)
        mock_paths.assert_called_once_with(scale=2.0)
        mock_points.assert_called_once_with(scale=2.0)
        mock_frame.assert_called_once()


def test_save(renderer):
    with patch('pathlib.Path.mkdir') as mock_mkdir, \
            patch('cairo.ImageSurface') as mock_surface_class:
        mock_surface_instance = MagicMock()
        mock_surface_class.return_value = mock_surface_instance

        # Replace the renderer's surface with our mock
        renderer.surface = mock_surface_instance

        renderer.save("test_file")

        mock_mkdir.assert_called_once()
        mock_surface_instance.write_to_png.assert_called_once()


def test_rotate(renderer):
    original_width = renderer.surface.get_width()
    original_height = renderer.surface.get_height()
    renderer.rotate(90)
    assert renderer.surface.get_width() == original_height
    assert renderer.surface.get_height() == original_width


def test_render_bb(renderer):
    bb = BoundingBox(10, 20, 30, 40)
    renderer.render_bb(bb)
    # Method should complete without error


def test_render_frame(renderer):
    renderer.render_frame()
    # Method should complete without error


def test_render_all_paths(renderer):
    mock_path = MagicMock(spec=Path)
    mock_path.as_tuple_list.return_value = [(0, 0), (10, 10)]
    mock_path.color = (255, 0, 0)
    mock_path.width = 1

    renderer.collection.add(mock_path)
    renderer.render_all_paths()
    # Method should complete without error


def test_render_all_points(renderer):
    mock_point = MagicMock(spec=Position)
    mock_point.properties = {Property.RADIUS: 5, Property.COLOR: (0, 255, 0)}
    mock_point.x = 50
    mock_point.y = 50

    renderer.positions.append(mock_point)
    renderer.render_all_points()
    # Method should complete without error


def test_render_points_with_outline(renderer):
    mock_point = MagicMock(spec=Position)
    mock_point.properties = {
        Property.RADIUS: 5,
        Property.COLOR: (0, 255, 0),
        "outline": (255, 0, 0)
    }
    mock_point.x = 50
    mock_point.y = 50

    renderer.render_points([mock_point], 1.0)
    # Method should complete without error


def test_clear(renderer):
    mock_path = MagicMock(spec=Path)
    mock_point = MagicMock(spec=Position)
    renderer.collection.add(mock_path)
    renderer.positions.append(mock_point)

    renderer.clear()
    assert len(renderer.collection.paths) == 0
    assert len(renderer.positions) == 0


def test_add_collection(renderer):
    mock_collection = MagicMock(spec=Collection)
    mock_collection.paths = [MagicMock(spec=Path)]
    renderer.add(mock_collection)
    assert len(renderer.collection.paths) == 1


def test_add_position(renderer):
    mock_position = MagicMock(spec=Position)
    renderer.add(mock_position)
    assert len(renderer.positions) == 1


def test_add_path(renderer):
    mock_path = MagicMock(spec=Path)
    renderer.add(mock_path)
    assert len(renderer.collection.paths) == 1
