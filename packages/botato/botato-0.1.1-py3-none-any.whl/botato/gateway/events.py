from typing import Callable, Awaitable, Dict, List, TypeVar, Any, get_type_hints
from loguru import logger
from pydantic import BaseModel

T = TypeVar("T", bound=Callable[..., Awaitable[None]])


class EventDispatcher:
    """
    Manages registration and dispatching of events.
    
    Event handlers must be async functions named like 'on_<event_name>'.
    """
    
    def __init__(self) -> None:
        self._handlers: Dict[str, List[T]] = {}
        
    def register(self, func: T) -> T:
        """
        Register an async event handler using its function name.

        Args:
            func (Callable): The handler coroutine function.

        Returns:
            Callable: The original function.
        """
        name = func.__name__
        if not name.startswith("on_"):
            raise ValueError("Event handler names must start with 'on_'")
        
        logger.debug(f"Registering event: {name}")
        self._handlers.setdefault(name, []).append(func)
        return func
    
    async def dispatch(self, event_name: str, payload: dict) -> None:
        """
        Call all handlers registered for the given event.
        
        If the handler expects a typed model (subclass of BaseModel),
        it will be instantiated with the payload data.

        Args:
            event_name (str): Event name from Discord
            payload (dict): Event payload data
        """
        handler_key = f"on_{event_name.lower()}"
        if handlers := self._handlers.get(handler_key):
            for handler in handlers:
                try:
                    hints = get_type_hints(handler)
                    if hints:
                        # Get the first parameter type hint
                        param_type = next(iter(hints.values()))
                        if isinstance(param_type, type) and issubclass(param_type, BaseModel):
                            parsed = param_type(**payload)
                            await handler(parsed)
                            continue
                        
                    # Fallback to raw dict if no model hint
                    await handler(payload)
                except Exception as e:
                    logger.exception(f"Error in handler '{handler_key}': {e}")
        else:
            logger.debug(f"No handlers for event: {handler_key}")