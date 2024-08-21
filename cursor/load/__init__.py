from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KeyPress:
    key: chr
    timestamp: float
    is_down: bool
