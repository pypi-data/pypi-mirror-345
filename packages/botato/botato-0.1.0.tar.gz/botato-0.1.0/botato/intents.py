import json
from pathlib import Path
from typing import Optional



class Intents:
    """
    Represents the Gateway Intents your bot will subscribe to.
    
    Use Intents.default() or Intents.all() to create configurations.
    Supports loading the official Discord mapping from a JSON file.
    """
    _intent_map: dict[str, dict] = {}
    _event_lookup: dict[str, str] = {}
    
    def __init__(self, value: int = 0) -> None:
        """
        Initialize an Intents object.
        
        Args:
            value (int): Bitwise OR of all enabled intents.
        """
        self.value = value
        self._load_intent_map()
        
    @classmethod
    def _load_intent_map(cls) -> None:
        """Load the intents and event mappings from the JSON file."""
        if cls._intent_map:
            return
        
        path = Path(__file__).parent / "data" / "intents.json"
        with path.open('r', encoding='utf-8') as f:
            raw = json.load(f)
            cls._intent_map = raw
            
            # Build reverse event -> intent lookup
            for intent_name, info in raw.items():
                for event in info["events"]:
                    cls._event_lookup[event] = intent_name
                    
    @classmethod
    def default(cls) -> "Intents":
        """Recommended default: GUILDS, GUILD_MESSAGES, MESSAGE_CONTENT"""
        cls._load_intent_map()
        return cls(
            cls._intent_value("GUILDS")
            | cls._intent_value("GUILD_MESSAGES")
            | cls._intent_value("MESSAGE_CONTENT")
        )
        
    @classmethod
    def all(cls) -> "Intents":
        """Enable all known intents (not recommended)."""
        cls._load_intent_map()
        total = 0
        for intent_name in cls._intent_map:
            total |= cls._intenet_value(intent_name)
        return cls(total)
    
    @classmethod
    def _intent_value(cls, name: str) -> int:
        """Get the 1 << bit value for an intent by name."""
        try:
            bit = cls._intent_map[name]["bit"]
            return 1 << bit
        except KeyError:
            raise ValueError(f"Unknown intent: {name}")
        
    def enable(self, name: str) -> None:
        """Enable an intent by name."""
        self.value |= self._intent_value(name)
        
    def disable(self, name: str) -> None:
        """Disable an intent by name."""
        self.value &= ~self._intent_value(name)
        
    def requires(self, event_name: str) -> Optional[str]:
        """
        Find which intent is required to receive a specific event.

        Args:
            event_name (str): Discord event name.

        Returns:
            str | None: Intent name, or None if unknown.
        """
        return self._event_lookup.get(event_name)
    
    def describe(self) -> dict[str, bool]:
        """
        Return a dictionary of all known intents and whether they are enabled.

        Returns:
            dict: { intent_name: enabled? }
        """
        return {
            name: bool(self.value & (1 << info["bit"]))
            for name, info in self._intent_map.items()
        }
        
    def __repr__(self) -> str:
        active = [k for k, v in self.describe().items() if v]
        return f"<Intents enabled={active}>"