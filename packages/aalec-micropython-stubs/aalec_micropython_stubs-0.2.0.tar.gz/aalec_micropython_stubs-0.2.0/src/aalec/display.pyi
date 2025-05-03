import machine
from aalec import constants as constants
from aalec.third_party import sh1106 as sh1106

class Display:
    """Display class.

    Args:
        i2c: A `machine.I2C` instance.
    """
    def __init__(self, i2c: machine.I2C) -> None: ...
    def print_line(self, line: int, text: str) -> None:
        """Print a line of text on the display.

        A line can be at most 16 characters long. (A character has a size of 8x8 pixels.)

        Args:
            line (int): Line number. Valid values are from 1 to 5.
            text (str): The content to display.
        """
    def clear_display(self) -> None:
        """Clear the display."""
    def rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        """Draw a rectangle frame on the display.

        Args:
            x (int): X coordinate of the upper left corner of the progressbar
            y (int): Y coordinate of the upper left corner of the progressbar
            width (int): Width of the progressbar in pixel. (x delta to the lower right corner.)
            height (int): Height of the progressbar in pixel. (y delta to the lower right corner.)
            color (int): Frame color (`constants.WHITE` or `constants.BLACK`)
        """
    def filled_rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        """Draw a filled rectangle on the display.

        Args:
            x (int): X coordinate of the upper left corner of the progressbar
            y (int): Y coordinate of the upper left corner of the progressbar
            width (int): Width of the progressbar in pixel. (x delta to the lower right corner.)
            height (int): Height of the progressbar in pixel. (y delta to the lower right corner.)
            color (int): Fill color (`constants.WHITE` or `constants.BLACK`)
        """
    def draw_progressbar(self, x: int, y: int, width: int, height: int, percent: int) -> None:
        """Draw a progressbar.

        Args:
            x (int): X coordinate of the upper left corner of the progressbar
            y (int): Y coordinate of the upper left corner of the progressbar
            width (int): Width of the progressbar in pixel. (x delta to the lower right corner.)
            height (int): Height of the progressbar in pixel. (y delta to the lower right corner.)
            percent (int): How many percent the bar is filled (grows to the right).
        """

def test_display() -> None:
    """Test for the display class."""
