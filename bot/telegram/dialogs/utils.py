"""
Утилиты для валидации ISIN (International Securities Identification Number)
"""
import re
from typing import Optional



def validate_isin_format(isin: str) -> tuple[bool, Optional[str]]:
    """
    Проверяет формат ISIN
    
    ISIN состоит из:
    - 2 буквы (код страны)
    - 9 букв/цифр (NSIN - National Securities Identifying Number)
    - 1 контрольная цифра
    Итого: 12 символов
    
    Args:
        isin: Строка для проверки
    
    Returns:
        Кортеж (валиден ли формат, сообщение об ошибке или None)
    """
    if not isin:
        return False, "ISIN не может быть пустым"
    
    isin_upper = isin.upper().strip()
    
    # Проверка длины
    if len(isin_upper) != 12:
        return False, f"ISIN должен содержать 12 символов, получено {len(isin_upper)}"
    
    # Проверка формата: первые 2 символа - буквы
    if not re.match(r'^[A-Z]{2}', isin_upper):
        return False, "Первые 2 символа ISIN должны быть буквами (код страны)"
    
    if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}', isin_upper):
        return False, "Символы с 3 по 11 должны быть буквами или цифрами"
    
    if not isin_upper[11].isdigit():
        return False, "Последний символ ISIN должен быть цифрой (контрольная сумма)"
    
    return True, None


def is_isin_like(text: str) -> bool:
    """
    Быстрая проверка, похоже ли на ISIN (только формат, без проверки контрольной суммы)
    
    Args:
        text: Строка для проверки
    
    Returns:
        True если похоже на ISIN, False иначе
    """
    is_valid, _ = validate_isin_format(text)
    return is_valid


# Функции для работы с TinkoffOrderBook удалены

