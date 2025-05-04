"""
Math utilities for color calculations.
"""

from typing import Tuple

def compute_XZ(x: float, y: float, Y: float) -> Tuple[float, float]:
    if y == 0:
        raise ValueError("y cannot be zero for tristimulus calculation")
    factor = Y / y
    return x * factor, (1 - x - y) * factor


def compute_uv_prime(X: float, Y: float, Z: float) -> Tuple[float, float]:
    denom = X + 15 * Y + 3 * Z
    if denom == 0:
        return 0.0, 0.0
    return 4 * X / denom, 9 * Y / denom
