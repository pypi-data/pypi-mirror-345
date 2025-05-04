"""
Base Engine Module

Defines the abstract BaseEngine class for function engines.
"""

from abc import ABC, abstractmethod

from apilot.core.event import EventEngine


class BaseEngine(ABC):
    """
    Abstract class for implementing a function engine.
    """
    def __init__(
        self,
        main_engine,
        event_engine: EventEngine,
        engine_name: str,
    ) -> None:
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.engine_name = engine_name

    @abstractmethod
    def close(self):
        pass
