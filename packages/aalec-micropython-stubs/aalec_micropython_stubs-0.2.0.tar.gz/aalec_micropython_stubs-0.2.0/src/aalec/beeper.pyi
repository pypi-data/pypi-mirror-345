from aalec import constants as constants

class Beeper:
    """Beeper.

    Args:
        pin (int): The pin the beeper is connected to.
    """
    def __init__(self, pin: int) -> None: ...
    def play(self, freq: int, dur: int | None = None) -> None:
        """Play a tone.

        Args:
            freq (int): The frequency of the tone. If the frequency is <=0, no tone will be played.
            dur (int | None, optional): Duration of the tone in ms.
                If set to `None` the tone will keep playing. Defaults to None.
        """

def test_beeper() -> None:
    """Test for the beeper class."""
