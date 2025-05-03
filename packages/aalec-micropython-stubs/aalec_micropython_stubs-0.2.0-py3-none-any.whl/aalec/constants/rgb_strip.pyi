from _typeshed import Incomplete
from typing import NamedTuple

class RgbColor(NamedTuple('RgbColorBase', [('r', Incomplete), ('g', Incomplete), ('b', Incomplete)])):
    """RGB Color.

    Attributes:
        r (int): red part of the color. (0-255)
        g (int): green part of the color. (0-255)
        b (int): blue part of the color. (0-255)
    """

LED_COUNT: int
DIM: int
MEDIUM: int
BRIGHT: int
c_off: RgbColor
c_red: RgbColor
c_green: RgbColor
c_blue: RgbColor
c_yellow: RgbColor
c_white: RgbColor
c_cyan: RgbColor
c_purple: RgbColor
