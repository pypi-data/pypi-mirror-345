import abc
from _typeshed import Incomplete as Incomplete
from abc import abstractmethod
from framebuf import FrameBuffer
from machine import I2C as I2C, Pin as Pin, SPI as SPI
from typing import overload

class SH1106(FrameBuffer, metaclass=abc.ABCMeta):
    """
    Base class for SH1106 OLED display drivers.
    Handles common functionality such as rendering, power management, and drawing operations.
    """
    def __init__(self, width: int, height: int, external_vcc: bool, rotate: int = 0) -> None:
        """
        Initialize the SH1106 driver.

        :param width: Display width in pixels.
        :param height: Display height in pixels.
        :param external_vcc: Whether to use external VCC (True) or internal (False).
        :param rotate: Rotation angle (0, 90, 180, 270 degrees).
        """
    @abstractmethod
    def write_cmd(self, *args, **kwargs) -> Incomplete: ...
    @abstractmethod
    def write_data(self, *args, **kwargs) -> Incomplete: ...
    def init_display(self) -> None:
        """Initialize and reset the display."""
    def poweroff(self) -> None:
        """Turn off the display."""
    def poweron(self) -> None:
        """Turn on the display."""
    def flip(self, flag: bool | None = None, update: bool = True) -> None:
        """
        Flip the display horizontally or vertically.

        :param flag: If True, enable flipping; if False, disable.
        :param update: Whether to update the display immediately.
        """
    def rotate(self, flag: bool | None = None, update: bool = True) -> None:
        """
        Flip the display horizontally or vertically.

        :param flag: If True, enable flipping; if False, disable.
        :param update: Whether to update the display immediately.
        """
    def sleep(self, value: bool) -> None:
        """
        Put the display into sleep mode or wake it up.

        :param value: True to sleep, False to wake up.
        """
    def contrast(self, contrast: int) -> None:
        """
        Set the display contrast level.

        :param contrast: Contrast value (0-255).
        """
    def invert(self, invert: bool) -> None:
        """
        Invert the display colors.

        :param invert: True to invert, False to reset to normal.
        """
    def show(self, full_update: bool = False) -> None:
        """
        Refresh the display with the current buffer content.

        :param full_update: If True, update all pages; otherwise, update only modified pages.
        """
    @overload
    def pixel(self, x: int, y: int, /) -> int:
        """
        Get or set the color of a specific pixel.

        :param x: X-coordinate.
        :param y: Y-coordinate.
        :param color: Pixel color (0 or 1). If None, return the current color.
        """
    @overload
    def pixel(self, x: int, y: int, color: int) -> None:
        """
        Get or set the color of a specific pixel.

        :param x: X-coordinate.
        :param y: Y-coordinate.
        :param color: Pixel color (0 or 1). If None, return the current color.
        """
    def text(self, text: str, x: int, y: int, color: int = 1) -> None:
        """
        Draw text on the display.

        :param text: String to draw.
        :param x: X-coordinate of the top-left corner.
        :param y: Y-coordinate of the top-left corner.
        :param color: Text color (1 for white, 0 for black).
        """
    def line(self, x0: int, y0: int, x1: int, y1: int, color: int) -> None:
        """Draw a line between two points."""
    def hline(self, x: int, y: int, w: int, color: int) -> None:
        """Draw a horizontal line."""
    def vline(self, x: int, y: int, h: int, color: int) -> None:
        """Draw a vertical line."""
    def fill(self, color: int) -> None:
        """Fill the entire display with a single color."""
    def blit(self, fbuf: FrameBuffer, x: int, y: int, key: int = -1, palette: bytes | None = None) -> None:
        """
        Copy a framebuffer onto the display.

        :param fbuf: Source framebuffer.
        :param x: X-coordinate for placement.
        :param y: Y-coordinate for placement.
        :param key: Transparent color key.
        :param palette: Optional color palette for translation.
        """
    def scroll(self, x: int, y: int) -> None:
        """Scroll the display content by a certain amount."""
    def fill_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        """Draw a filled rectangle."""
    def rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        """Draw an outlined rectangle."""
    def ellipse(self, x: int, y: int, xr: int, yr: int, color: int) -> None:
        """Draw an outlined ellipse."""
    def reset(self, res: Pin | None = None) -> None:
        """Reset the display using the reset pin."""

class SH1106_I2C(SH1106):
    """
    SH1106 driver for I2C communication.
    """
    def __init__(self, width: int, height: int, i2c: I2C, res: Pin | None = None, addr: int = 60, rotate: int = 0, external_vcc: bool = False, delay: int = 0) -> None:
        """
        Initialize the SH1106 I2C driver.
        """
    def write_cmd(self, cmd: int) -> None:
        """Write a command to the display via I2C."""
    def write_data(self, buf: bytes) -> None:
        """Write data to the display via I2C."""
    def reset(self, res: Pin | None = None) -> None:
        """Reset the display via the reset pin (if available)."""

class SH1106_SPI(SH1106):
    """
    SH1106 driver for SPI communication.
    """
    def __init__(self, width: int, height: int, spi: SPI, dc: Pin, res: Pin | None = None, cs: Pin | None = None, rotate: int = 0, external_vcc: bool = False, delay: int = 0) -> None:
        """
        Initialize the SH1106 SPI driver.
        """
    def write_cmd(self, cmd: int) -> None:
        """Write a command to the display via SPI."""
    def write_data(self, buf: bytes) -> None:
        """Write data to the display via SPI."""
    def reset(self, res: Pin | None = None) -> None:
        """Reset the display via the reset pin (if available)."""
