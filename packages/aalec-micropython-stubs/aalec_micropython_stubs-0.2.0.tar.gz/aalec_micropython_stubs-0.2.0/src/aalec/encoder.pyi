class Encoder:
    """Convert encoder value to integer.

    Args:
        track_1 (int): The pin the track_1 of the encoder is connected to.
        track_2 (int): The pin the track_2 of the encoder is connected to.
    """
    def __init__(self, track_1: int, track_2: int) -> None: ...
    def get_rotate(self) -> int:
        """Get the rotary encoder value.

        Returns:
            int: Value of the rotary encoder.
        """
    def rotate_changed(self) -> bool:
        """Indicate if the encoder value changed since last call to this method.

        Returns:
            bool: True if the value changed since last call. False otherwise.
        """
    def reset_rotate(self, value: int) -> None:
        """Reset rotary encoder value.

        Args:
            value (int): new value for the rotary encoder.
        """

def test_encoder() -> None:
    """Test for the encoder class."""
