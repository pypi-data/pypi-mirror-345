from botato.models.base import BotatoBase
from datetime import datetime


DISCORD_EPOCH = 1420070400000

class Snowflake(str):
    """
    Represents a Discord Snowflake ID.

    Internally, it's a string, but this gives semantic meaning
    and allows for future helpers like `.timestamp()` or `.as_int()`.
    """

    def __new__(cls, value: str | int) -> "Snowflake":
        if isinstance(value, int):
            value = str(value)
        elif not isinstance(value, str):
            raise TypeError("Snowflake must be initialized with a string or integer")
        if not value.isdigit():
            raise ValueError("Snowflake must be numeric")
        return super().__new__(cls, value)
    
    def as_int(self) -> int:
        """Return the snowflake as an integer."""
        return int(self)
    
    def timestamp(self) -> datetime:
        """
        Return the Discord timestamp from the snowflake bits.

        Snowflake format:
        - 42 bits: timestamp offset from Discord Epoch
        - 22 bits: internal worker/process IDs and increment
        """
        timestamp_ms = (int(self) >> 22) + DISCORD_EPOCH
        return datetime.fromtimestamp(timestamp_ms / 1000)
    
    def __int__(self) -> int:
        return self.as_int()
    
    def __repr__(self) -> str:
        return f"Snowflake({super().__repr__()})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, (str, int)):
            return int(self) == int(other)
        return super().__eq__(other)
    
    def __hash__(self) -> int:
        return hash(int(self))