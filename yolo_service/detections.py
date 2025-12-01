from dataclasses import dataclass


@dataclass
class Detection:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
