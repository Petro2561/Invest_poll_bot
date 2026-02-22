from enum import StrEnum, auto


class EventType(StrEnum):
    """Тип события для отслеживания"""
    ORDERBOOK = auto()  # Отслеживание заявок в стакане
    TRADE = auto()  # Свершившиеся сделки

