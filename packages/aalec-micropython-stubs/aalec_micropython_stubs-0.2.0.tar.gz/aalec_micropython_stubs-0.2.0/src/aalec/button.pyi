from aalec import constants as constants

class Button:
    """Button class.

    Args:
        button_pin (int): The pin the button of the encoder is connected to.
    """
    def __init__(self, button_pin: int) -> None: ...
    def get_button(self) -> int:
        """Get the button value.

        Returns:
            int: Value of the button. Button pressed: `1`. Button released: `0`.
        """
    def button_changed(self) -> bool:
        """Indicates if the button value changed since the last call to this method.

        Returns:
            bool: `True` if the value has changed since the last call. `False` otherwise.
        """

def test_button(button_pin: int) -> None:
    """Test for the Button class.

    Args:
        button_pin (int): The pin the button of the encoder is connected to.
    """
