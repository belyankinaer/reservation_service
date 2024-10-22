from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy.orm import sessionmaker
from app.logging_config import setup_logging
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, update, func, text
from fastapi import HTTPException

from app.constants import DATABASE_URL, DATABASE_URL_2
from app.models import Product, Reservation, Base
from app.utils import async_session_decorator

#engine = create_engine(DATABASE_URL) #правильные настройки

engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class DatabaseManager:
    """Класс для работы с базой данных."""

    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.session = AsyncSession()

    async def get_db(self):
        """Функция для получения сессии базы данных."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def create_database(self):
        engine = create_async_engine(DATABASE_URL_2, echo=True)
        async with engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname='reservation_service'"))
            if not result.fetchone():
                await conn.execute(text("CREATE DATABASE reservation_service;"))
                print("Database 'reservation_service' created successfully.")
            else:
                print("Database 'reservation_service' already exists.")

    @async_session_decorator()
    async def create_tables(self, session):  # Updated method signature
        """Создание таблиц в базе данных reservation_service."""
       #todo проверить создание продуктов потому что они как будто пересоздаются

        create_products_table = """
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    product_id VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(100),
                    quantity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """

        create_reservations_table = """
                CREATE TABLE IF NOT EXISTS reservations (
                    id SERIAL PRIMARY KEY,
                    reservation_id VARCHAR(50) NOT NULL UNIQUE,
                    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
                    quantity INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending'
                );
                """
        try:
            await session.execute(text(create_products_table))
            await session.execute(text(create_reservations_table))

            self.logger.info("Таблицы 'products','reservations' успешно созданы или уже существуют.")
        except SQLAlchemyError as e:
            self.logger.info(f"Ошибка при добавлении таблиц: {e}")

    @async_session_decorator()
    async def add_product(self,product_id: str, name: str, quantity: int, session):
        """Добавление нового продукта в таблицу products."""
        #todo нужно добавить проверку на то есть ли объект в бд и если есть то не обновлять
        insert_product_query = text("""
            INSERT INTO products (product_id, name, quantity)
            VALUES (:product_id, :name, :quantity)
            ON CONFLICT (product_id) DO UPDATE 
            SET name = EXCLUDED.name,
                quantity = EXCLUDED.quantity;
        """)

        try:
            await session.execute(insert_product_query, {
                "product_id": product_id,
                "name": name,
                "quantity": quantity
            })
            self.logger.info(f"Продукт '{name}' c id '{product_id}' успешно добавлен.")
        except SQLAlchemyError as e:
            self.logger.info(f"Ошибка при добавлении продукта c id '{product_id}': {e}")


