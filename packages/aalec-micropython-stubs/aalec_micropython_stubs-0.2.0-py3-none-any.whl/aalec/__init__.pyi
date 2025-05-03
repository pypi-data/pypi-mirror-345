from aalec import constants as constants

__all__ = ['constants', 'AALeC']

class AALeC:
    """Proxy class to implement the AALeC API."""
    def __init__(self) -> None: ...
    def id(self) -> str:
        """A unique ID for this board.

        Returns:
            str: The unique ID for this board.
        """
    def get_analog(self) -> int:
        """Get value from analog pin.

        Returns:
            int: Value of the 10 bit ADC (0-1024)
        """
    def play(self, freq: int, dur: int | None = None) -> None:
        """Proxy for [`Beeper.play`](beeper.md#aalec.beeper.Beeper.play).

        Args:
            freq (int): The frequency of the tone. If the frequency is <=0, no tone will be played.
            dur (int | None, optional): Duration of the tone in ms.
                If set to `None` the tone will keep playing. Defaults to None.
        """
    def get_button(self) -> int:
        """Proxy for [`Button.get_button`](button.md#aalec.button.Button.get_button).

        Returns:
            int: Value of the button. Button pressed: `1`. Button released: `0`.
        """
    def button_changed(self) -> bool:
        """Proxy for [`Button.button_change`](button.md#aalec.button.Button.button_changed).

        Returns:
            bool: `True` if the value has changed since the last call. `False` otherwise.
        """
    def print_line(self, line: int, text: str) -> None:
        """Proxy for [`Display.print_line`](display.md#aalec.display.Display.print_line).

        A line can be at most 16 characters long. (A character has a size of 8x8 pixels.)

        Args:
            line (int): Line number. Valid values are from 1 to 5.
            text (str): The content to display.
        """
    def clear_display(self) -> None:
        """Proxy for [`Display.clear_display`](display.md#aalec.display.Display.clear_display)."""
    def rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        """Proxy for [`Display.rect`](display.md#aalec.display.Display.rect).

        Args:
            x (int): X coordinate of the upper left corner of the progressbar
            y (int): Y coordinate of the upper left corner of the progressbar
            width (int): Width of the progressbar in pixel. (x delta to the lower right corner.)
            height (int): Height of the progressbar in pixel. (y delta to the lower right corner.)
            color (int): Frame color (`constants.WHITE` or `constants.BLACK`)
        """
    def filled_rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        """Proxy for [`Display.filled_rect`](display.md#aalec.display.Display.filled_rect).

        Args:
            x (int): X coordinate of the upper left corner of the progressbar
            y (int): Y coordinate of the upper left corner of the progressbar
            width (int): Width of the progressbar in pixel. (x delta to the lower right corner.)
            height (int): Height of the progressbar in pixel. (y delta to the lower right corner.)
            color (int): Fill color (`constants.WHITE` or `constants.BLACK`)
        """
    def draw_progressbar(self, x: int, y: int, width: int, height: int, percent: int) -> None:
        """Proxy for [`Display.draw_progressbar`](display.md#aalec.display.Display.draw_progressbar).

        Args:
            x (int): X coordinate of the upper left corner of the progressbar
            y (int): Y coordinate of the upper left corner of the progressbar
            width (int): Width of the progressbar in pixel. (x delta to the lower right corner.)
            height (int): Height of the progressbar in pixel. (y delta to the lower right corner.)
            percent (int): How many percent the bar is filled (grows to the right).
        """
    def get_rotate(self) -> int:
        """Proxy for [`Encoder.get_rotate`](encoder.md#aalec.encoder.Encoder.get_rotate).

        Returns:
            int: Value of the rotary encoder.
        """
    def rotate_changed(self) -> bool:
        """Proxy for [`Encoder.rotate_changed`](encoder.md#aalec.encoder.Encoder.rotate_changed).

        Returns:
            bool: True if the value changed since last call. False otherwise.
        """
    def reset_rotate(self, value: int) -> None:
        """Proxy for [`Encoder.reset_rotate`](encoder.md#aalec.encoder.Encoder.reset_rotate).

        Args:
            value (int): new value for the rotary encoder.
        """
    def get_environment_sensor(self) -> str:
        '''Proxy for [`Environment.get_environment_sensor`](environment.md#aalec.environment.Environment.get_environment_sensor).

        Returns:
            str: "BMP280"
        '''
    def get_temp(self) -> float:
        """Proxy for [`Environment.get_temp`](environment.md#aalec.environment.Environment.get_temp).

        Returns:
            float: Current temperature in °C.
        """
    def get_humidity(self) -> float:
        """Proxy for [`Environment.get_humidity`](environment.md#aalec.environment.Environment.get_humidity).

        Returns:
            float: 0.0 (BMP280 doesn't have a humidity sensor).
        """
    def get_pressure(self) -> float:
        """Proxy for [`Environment.get_pressure`](environment.md#aalec.environment.Environment.get_pressure).

        Returns:
            float: current pressure in hPa.
        """
    def get_gas_resistance(self) -> float:
        """Proxy for [`Environment.get_gas_resistance`](environment.md#aalec.environment.Environment.get_gas_resistance).

        Returns:
            float: 0.0 (BMP280 doesn't have a gas resistance sensor).
        """
    def set_rgb_led(self, led: int, color: constants.RgbColor) -> None:
        """Proxy for [`RgbStrip.set_rgb_led`](rgb_strip.md#aalec.rgb_strip.RgbStrip.set_rgb_led).

        Args:
            led (int): Index of the led in the strip (starts with 0).
            color (RgbColor): The color to set

        Raises:
            AttributeError: If the `led` value does not address a led in the strip.
        """
    def set_rgb_strip(self, colors: list[constants.RgbColor]) -> None:
        """Proxy for [`RgbStrip.set_rgb_strip`](rgb_strip.md#aalec.rgb_strip.RgbStrip.set_rgb_strip).

        Args:
            colors (list[RgbColor]): A list of colors.

        Raises:
            AttributeError: If the length of the list of colors is not
                exactly the number of leds in the strip.
        """
    def reset_rgb_strip(self) -> None:
        """Proxy for [`RgbStrip.reset`](rgb_strip.md#aalec.rgb_strip.RgbStrip.reset)."""
