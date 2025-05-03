import machine

class Environment:
    """Environment class.

    Args:
        i2c: A `machine.I2C` instance.
        addr: The i2c address of the sensor.
    """
    def __init__(self, i2c: machine.I2C, addr: int) -> None: ...
    def get_environment_sensor(self) -> str:
        '''Get type of environment sensor

        Returns:
            str: "BMP280"
        '''
    def get_temp(self) -> float:
        """Get current Temperature.

        Returns:
            float: Current temperature in °C.
        """
    def get_humidity(self) -> float:
        """Get current humidity.

        Returns:
            float: 0.0 (BMP280 doesn't have a humidity sensor).
        """
    def get_pressure(self) -> float:
        """Get current pressure in hPa.

        Returns:
            float: current pressure in hPa.
        """
    def get_gas_resistance(self) -> float:
        """Get gas resistance.

        Returns:
            float: 0.0 (BMP280 doesn't have a gas resistance sensor).
        """

def test_environment() -> None:
    """Test for the environment class."""
