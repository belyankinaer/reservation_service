from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy.orm import sessionmaker
from app.logging_config import setup_logging
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, update, func, text
from fastapi import HTTPException

from app.constants import DATABASE_URL
from app.models import Product, Reservation


#engine = create_engine(DATABASE_URL) #правильные настройки

engine = create_engine('postgresql://postgres:admin@localhost:5432/postgres', isolation_level="AUTOCOMMIT")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class DatabaseManager:
    """Класс для работы с базой данных."""

    def __init__(self):
        """Инициализация класса"""
        setup_logging()
        self.logger = logging.getLogger(__name__)

    async def get_db(self):
        """Функция для получения сессии базы данных."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def execute_query(self, query, params=None):
        """Выполняет произвольный SQL-запрос."""
        result = self.session.execute(query, params or {})
        return result.fetchall()

    async def get(self, model, **kwargs):
        """Получает объект по заданным параметрам."""
        return self.session.query(model).filter_by(**kwargs).first()

    async def add(self, instance):
        """Добавляет новый объект в базу данных."""
        self.session.add(instance)
        self.session.commit()
        return instance

    async def update(self,insert_query, instance):
        """Обновляет существующий объект."""
        if not insert_query:
            insert_query = self.gen_query_for_update_o(table_name=instance.__tablename__, fields=instance.__dict__,
                                                       type_o=type(instance).__name__)

        self.session.execute(insert_query, instance)
        self.session.commit()
        return instance

    async def gen_query_for_update_o(self, table_name, fields, type_o):
        """
                Генерирует SQL-запрос для вставки или обновления данных в указанной таблице.

                :param table_name: Имя таблицы.
                :param fields: Словарь с полями и их значениями.
                :return: Сформированный SQL-запрос.
                """
        columns = ', '.join(fields.keys())
        placeholders = ', '.join(f":{key}" for key in fields.keys())

        update_clause = ', '.join(f"{key} = EXCLUDED.{key}" for key in fields.keys())

        query = f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({placeholders})
                    ON CONFLICT ({type_o.lower()}_id) DO UPDATE 
                    SET {update_clause};
                """

        return query



    def create_database(self):
        """Создание базы данных reservation_service (если это необходимо)."""
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 FROM pg_database WHERE datname='reservation_service'"))
            if not result.fetchone():
                connection.execute(text("CREATE DATABASE reservation_service;"))
                self.logger.info("База данных 'reservation_service' успешно создана.")
            else:
                self.logger.info("База данных 'reservation_service' уже существует.")


    def create_tables(self):
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

        with engine.connect() as connection:
            connection.execute(text(create_products_table))
            connection.execute(text(create_reservations_table))
            self.logger.info("Таблицы 'products','reservations' успешно созданы или уже существуют.")
    ###todo: Base.metadata.create_all(engine)

    def add_product(self,product_id: str, name: str, quantity: int):
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
            with engine.connect() as connection:

                with connection.begin():
                    connection.execute(insert_product_query, {
                        "product_id": product_id,
                        "name": name,
                        "quantity": quantity
                    })
            self.logger.info(f"Продукт '{name}' c id '{product_id}' успешно добавлен.")
        except SQLAlchemyError as e:
            self.logger.info(f"Ошибка при добавлении продукта c id '{product_id}': {e}")


