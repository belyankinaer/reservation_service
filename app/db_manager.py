import logging

from app.logging_config import setup_logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from app.constants import URL_POSTGRES
from app.utils import async_session_decorator


class DatabaseManager:
    """Класс для работы с базой данных."""

    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.session = AsyncSession()

    async def create_database(self):
        engine = create_async_engine(URL_POSTGRES, echo=True)
        try:
            async with engine.connect() as conn:
                await conn.execution_options(isolation_level="AUTOCOMMIT")
                result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname='reservation_service'"))
                if not result.fetchone():
                    await conn.execute(text("CREATE DATABASE reservation_service;"))
                    self.logger.info("Database 'reservation_service' created successfully.")
                else:
                    self.logger.info("Database 'reservation_service' already exists.")
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating database: {e}")

    @async_session_decorator()
    async def create_tables(self, session):
        """Создание таблиц в базе данных reservation_service."""

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
    async def add_product(self, product_id: str, name: str, quantity: int, session):
        """Добавление нового продукта в таблицу products."""
        # Проверка на существование продукта
        existing_product_query = text("""
            SELECT COUNT(*) FROM products WHERE product_id = :product_id
        """)

        result = await session.execute(existing_product_query, {"product_id": product_id})
        count = result.scalar()

        if count > 0:
            self.logger.info(f"Продукт с id '{product_id}' уже существует.")
            return

        insert_product_query = text("""
            INSERT INTO products (product_id, name, quantity)
            VALUES (:product_id, :name, :quantity);
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
