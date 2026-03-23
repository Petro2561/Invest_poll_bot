# Управление базой данных

Проект использует **Alembic** для управления миграциями базы данных.

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных

**Вариант A: Использование Alembic (рекомендуется)**

```bash
# Создать первую миграцию
alembic revision --autogenerate -m "Initial migration"

# Применить миграции
alembic upgrade head
```

**В Docker** (из хоста, контейнер бота):

```bash
docker exec -it telegram-bot-quiz bash -c "cd /app && python -m alembic upgrade head"
```

Скрипты миграций лежат в каталоге `alembic_migrations/` (так он не конфликтует с пакетом `alembic` из PyPI при запуске `python -m alembic` из `/app`).

**Вариант B: Использование CLI утилиты**

```bash
# Создать все таблицы (без миграций)
python manage.py init-db

# Или использовать Alembic через manage.py
python manage.py makemigrations -m "Initial migration"
python manage.py migrate
```

**Вариант C: Прямое создание (только для разработки)**

```bash
python init_db.py
```

## Работа с миграциями

### Создание новой миграции

```bash
# Автоматическое определение изменений
alembic revision --autogenerate -m "описание изменений"

# Или через manage.py
python manage.py makemigrations -m "описание изменений"
```

### Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Или через manage.py
python manage.py migrate
```

### Откат миграций

```bash
# Откатить последнюю миграцию
alembic downgrade -1

# Откатить до конкретной ревизии
alembic downgrade <revision>

# Или через manage.py
python manage.py rollback
```

### Просмотр информации

```bash
# Текущая версия
alembic current

# История миграций
alembic history

# Или через manage.py
python manage.py current
python manage.py history
```

## Доступные команды manage.py

```bash
python manage.py init-db          # Создать все таблицы
python manage.py drop-db           # Удалить все таблицы (ОПАСНО!)
python manage.py makemigrations    # Создать миграцию
python manage.py migrate           # Применить миграции
python manage.py rollback          # Откатить миграции
python manage.py current           # Показать текущую версию
python manage.py history           # Показать историю
```

## Рекомендации

1. **Используйте Alembic** для продакшена и командной работы
2. **Не используйте** автоматическое создание таблиц в админке
3. **Всегда создавайте миграции** при изменении моделей
4. **Проверяйте миграции** перед применением в продакшене

## Структура миграций

Миграции хранятся в `alembic_migrations/versions/` и имеют формат:
```
<revision>_<description>.py
```

Пример: `a1b2c3d4e5f6_initial_migration.py`
