from enum import StrEnum, auto


class ActionType(StrEnum):
    """Тип действия - сторона стакана"""
    BIDS = auto()  # Заявки на покупку
    ASKS = auto()  # Заявки на продажу

