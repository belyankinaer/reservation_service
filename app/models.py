from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, info={'description': 'Уникальный идентификатор'})
    product_id = Column(String(50), unique=True, nullable=False, info= {'description': 'Идентификатор товара'})
    name = Column(String(100), nullable=False, info= {'description': 'Название'})
    quantity = Column(Integer, nullable=False, info= {'description': 'Количество на складе'})
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', info={'description': 'Дата создания'})
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP',
                        info={'description': 'Дата обновления'})

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, info={'description': 'Уникальный идентификатор'})
    reservation_id = Column(String(50), unique=True, nullable=False,
                            info= {'description': 'Идентификатор резервирования'})
    product_id = Column(String(50), ForeignKey('products.product_id'), nullable=False,
                        info={'description': 'Идентификатор продукта'})
    quantity = Column(Integer, nullable=False, info={'description': 'Количество резервированных единиц'})
    timestamp = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP',
                       info={'description': 'Время резервирования'})
    status = Column(String(20), default='pending', info={'description': 'Статус резервирования'})


model_mapping = {
    "Product": Product,
    "Reservation": Reservation,

}
