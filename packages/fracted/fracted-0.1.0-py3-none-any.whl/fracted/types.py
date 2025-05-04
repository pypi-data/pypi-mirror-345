"""This module contains types for using in type hints"""

from typing import Callable, Tuple

Point = Tuple[float, float]
TransformationLike = Callable[[Point], Point]
