from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)  # Уникальный идентификатор
    product_id = Column(String(50), unique=True, nullable=False)  # Идентификатор товара
    name = Column(String(100), nullable=False)  # Название товара
    quantity = Column(Integer, nullable=False)  # Количество на складе
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')  # Дата создания
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')  # Дата обновления

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)  # Уникальный идентификатор резервирования
    reservation_id = Column(String(50), unique=True, nullable=False)  # Идентификатор резервирования
    product_id = Column(String(50), ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)  # Количество зарезервированных единиц
    timestamp = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')  # Ensure timezone=True
    status = Column(String(20), default='pending')  # Статус резервирования

