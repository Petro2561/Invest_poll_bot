#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных (создание таблиц)
"""
import asyncio
from bot.config import load_config
from bot.services.database.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


async def init_database():
    """Создание всех таблиц в базе данных"""
    config = load_config()
    engine = create_async_engine(url=config.database.url, echo=True)
    
    print("Создание таблиц в базе данных...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
