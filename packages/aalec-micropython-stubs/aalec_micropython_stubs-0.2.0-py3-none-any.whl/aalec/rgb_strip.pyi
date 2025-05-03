from aalec import constants as constants

def set_intensity(color: constants.RgbColor, intensity: int = ...) -> constants.RgbColor:
    """Set the intensity of a color.

    Set the sum of the `r`,`g` and `b` values to `intensity`.

    Args:
        color (RgbColor): Color to balance
        intensity (int, optional): Overall intensity of the color (0 - 786). Defaults to MEDIUM.

    Returns:
        RgbColor: Balanced color.
    """

class RgbStrip:
    """Wrapper for neopixel strip.

    Args:
        pin (int): The pin the neopixel strip is connected to.
        n (int): Amount of pixels in the strip. Defaults to `LED_COUNT`.
    """
    def __init__(self, pin: int, n: int = ...) -> None: ...
    def set_rgb_led(self, led: int, color: constants.RgbColor) -> None:
        """Set one led of the rgb strip.

        Args:
            led (int): Index of the led in the strip (starts with 0).
            color (RgbColor): The color to set

        Raises:
            AttributeError: If the `led` value does not address a led in the strip.
        """
    def set_rgb_strip(self, colors: list[constants.RgbColor]) -> None:
        """Set all leds of the rgb strip at once.

        Args:
            colors (list[RgbColor]): A list of colors.

        Raises:
            AttributeError: If the length of the list of colors is not
                exactly the number of leds in the strip.
        """
    def reset(self) -> None:
        """Reset the strip and turns all leds off."""

def test_rbg_strip() -> None:
    """Test for the rgb strip class."""
