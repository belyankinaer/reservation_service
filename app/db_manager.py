from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://postgres:admin@localhost:5433/postgres"  #todo
engine = create_engine(DATABASE_URL)

from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Функция для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """Создание базы данных reservation_service (если это необходимо)."""
    with engine.connect() as connection:

        result = connection.execute(text("SELECT 1 FROM pg_database WHERE datname='reservation_service'"))
        if not result.fetchone():
            connection.execute(text("CREATE DATABASE reservation_service;"))
            print("База данных 'reservation_service' успешно создана.")
        else:
            print("База данных 'reservation_service' уже существует.")


def create_tables():
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
        print("Таблицы успешно созданы или уже существуют.")


def add_product(product_id: str, name: str, quantity: int):
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
        print(f"Продукт '{name}' успешно добавлен.")
    except SQLAlchemyError as e:
        print(f"Ошибка при добавлении продукта: {e}")
