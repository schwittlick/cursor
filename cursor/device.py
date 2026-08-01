from __future__ import annotations

import json
from enum import Enum, IntEnum, auto
from pathlib import Path
from typing import Dict, List, Tuple

from cursor.bb import BoundingBox as BB


class PlotterConfig:
    def __init__(self, type: PlotterType):
        self.type: PlotterType = type
        self.bb: BB = MinmaxMapping.maps[type]


class PlotterType(IntEnum):
    def __str__(self) -> str:
        return self.name

    ROLAND_DPX3300_A1 = auto()
    ROLAND_DPX3300_A2 = auto()
    ROLAND_DPX3300_A3 = auto()
    ROLAND_DPX3300_65_48 = auto()

    HP_7550A_A3 = auto()
    HP_7550A_A4 = auto()

    HP_7475A_A4 = auto()
    HP_7475A_A3 = auto()

    HP_7470A_A4 = auto()

    HP_DM_II_A0 = auto()
    HP_DM_II_A1 = auto()
    HP_DM_II_A3 = auto()

    HP_DM_SX_A0 = auto()
    HP_DM_SX_A1 = auto()
    HP_DM_SX_A3 = auto()

    HP_DM_RX_PLUS_A0 = auto()
    HP_DM_RX_PLUS_A1 = auto()
    HP_DM_RX_PLUS_A2 = auto()
    HP_DM_RX_PLUS_A3 = auto()
    HP_DM_RX_PLUS_1000x700 = auto()
    HP_DM_RX_PLUS_30x50 = auto()

    MUTOH_XP500_100x70cm = auto()
    MUTOH_XP500_102x72cm = auto()
    MUTOH_XP500_500x297mm = auto()
    MUTOH_XP500_A1 = auto()
    MUTOH_XP500_A2 = auto()
    MUTOH_XP500_A3 = auto()

    DIY_PLOTTER = auto()
    DIY_PLOTTER_A2 = auto()
    DIY_PLOTTER_A1 = auto()
    DIY_PLOTTER_100x59 = auto()
    DIY_PLOTTER_70x50 = auto()
    DIY_PLOTTER_60x60 = auto()
    DIY_PLOTTER_65x48 = auto()
    AXIDRAW = auto()

    ROLAND_DXY885 = auto()
    ROLAND_DXY980 = auto()
    ROLAND_DXY990 = auto()
    ROLAND_DXY1200_A3 = auto()
    ROLAND_DXY1200_A5 = auto()
    ROLAND_DXY1200_A3_EXPANDED = auto()
    ROLAND_DXY1300 = auto()

    ROLAND_PNC1000 = auto()
    ROLAND_PNC1000_50x100 = auto()

    TEKTRONIX_4662 = auto()
    DIGIPLOT_A1 = auto()
    HP_7570A_A1 = auto()
    GRAPHTEC_MP2000 = auto()
    GRAPHTEC_MP3100 = auto()


class ExportFormat(Enum):
    JPG = auto()
    SVG = auto()
    GCODE = auto()
    HPGL = auto()
    TEK = auto()
    DIGI = auto()


class PaperSize(Enum):
    PORTRAIT_36_48 = auto()
    LANDSCAPE_48_36 = auto()
    PORTRAIT_42_56 = auto()
    LANDSCAPE_56_42 = auto()
    PORTRAIT_50_70 = auto()
    LANDSCAPE_70_50 = auto()
    SQUARE_70_70 = auto()
    PORTRAIT_70_100 = auto()
    LANDSCAPE_100_70 = auto()
    LANDSCAPE_A4 = auto()
    PORTRAIT_A4 = auto()
    LANDSCAPE_A1 = auto()
    LANDSCAPE_A0 = auto()
    PORTRAIT_A3 = auto()
    LANDSCAPE_A3 = auto()
    LANDSCAPE_80_50 = auto()
    PORTRAIT_50_80 = auto()
    LANDSCAPE_A2 = auto()
    SQUARE_59_59 = auto()
    SQUARE_25_25 = auto()
    LANDSCAPE_A1_HP_7596B = auto()
    PORTRAIT_50_100 = auto()
    PHOTO_PAPER_240_178_LANDSCAPE = auto()
    PHOTO_PAPER_250_200_LANDSCAPE = auto()
    PHOTO_PAPER_400_300_LANDSCAPE = auto()
    PHOTO_PAPER_600_500_LANDSCAPE = auto()


# The enums above are the stable identifiers. Everything below is data, and it lives in
# data/plotters.json so that other software (e.g. hpgl-viewer) can read the same registry.
# Edit that file to change a plotter's area, margin, factors, speed or buffer size.

PLOTTER_REGISTRY_PATH = Path(__file__).parent / "data" / "plotters.json"


def _load_registry(path: Path = PLOTTER_REGISTRY_PATH) -> Dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


_registry = _load_registry()
_plotters: List[Dict] = _registry["plotters"]
_papers: List[Dict] = _registry["paper_sizes"]


def _bb(bounds: Dict[str, float]) -> BB:
    return BB(bounds["x"], bounds["y"], bounds["x2"], bounds["y2"])


def _plot_area(plotter: Dict) -> BB:
    """The plotter's maximum area, inset by its margin.

    A positive margin pulls that edge inward, a negative one pushes it past the machine
    maximum. The margins are hand-tuned, mostly for aesthetic paper padding; MaxArea.maps
    exposes the unmargined maximum.
    """
    area = _bb(plotter["max_area"])
    margin = plotter.get("margin")
    if not margin:
        return area
    return BB(
        area.p1.x + margin.get("left", 0),
        area.p1.y + margin.get("bottom", 0),
        area.p2.x - margin.get("right", 0),
        area.p2.y - margin.get("top", 0),
    )


def _hpgl_names() -> Dict[str, List[PlotterType]]:
    """Group plotters by the HPGL model they report.

    Callers rely on the first entry being the expected default config for that model
    (see serial_powertools), so plotters flagged "default_for_model" are sorted first.
    """
    grouped: Dict[str, List[Dict]] = {}
    for p in _plotters:
        if "hpgl_model" in p:
            grouped.setdefault(p["hpgl_model"], []).append(p)
    return {
        model: [PlotterType[p["id"]] for p in sorted(ps, key=lambda p: not p.get("default_for_model", False))]
        for model, ps in grouped.items()
    }


class ExportFormatMappings:
    maps: Dict[PlotterType, ExportFormat] = {
        PlotterType[p["id"]]: ExportFormat[p["export_format"]] for p in _plotters if "export_format" in p
    }


class MaxArea:
    """The plotter's maximum plot area, before the margin applied in MinmaxMapping."""

    maps: Dict[PlotterType, BB] = {PlotterType[p["id"]]: _bb(p["max_area"]) for p in _plotters if "max_area" in p}


class MinmaxMapping:
    """The effective plot area: MaxArea inset by the plotter's margin."""

    maps: Dict[PlotterType, BB] = {PlotterType[p["id"]]: _plot_area(p) for p in _plotters if "max_area" in p}


class PlotterName:
    names: Dict[PlotterType, str] = {PlotterType[p["id"]]: p["name"] for p in _plotters if "name" in p}


class PlotterHpglNames:
    names: Dict[str, List[PlotterType]] = _hpgl_names()


class XYFactors:
    fac: Dict[PlotterType, Tuple[float, float]] = {
        PlotterType[p["id"]]: (p["units_per_mm"]["x"], p["units_per_mm"]["y"]) for p in _plotters if "units_per_mm" in p
    }


class MaxSpeed:
    fac: Dict[PlotterType, int] = {PlotterType[p["id"]]: p["max_speed"] for p in _plotters if "max_speed" in p}


class BufferSize:
    # Default buffer sizes. Can be changed
    fac: Dict[PlotterType, int] = {PlotterType[p["id"]]: p["buffer_size"] for p in _plotters if "buffer_size" in p}


class PaperSizeName:
    names: Dict[PaperSize, str] = {PaperSize[p["id"]]: p["name"] for p in _papers if "name" in p}


class Paper:
    sizes: Dict[PaperSize, BB] = {PaperSize[p["id"]]: _bb(p["bounds"]) for p in _papers if "bounds" in p}
