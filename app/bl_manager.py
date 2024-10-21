import logging
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update, func
from fastapi import HTTPException

from app.logging_config import setup_logging
from app.models import Product
from app.utils import async_session_decorator


# todo добавить проверку что резервицая с там айди уже есть
# todo проверка что такого продукта нет

class BLManager:

    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.session  = AsyncSession()


    @async_session_decorator()
    async def reserve_item(self, reservation_id: str, product_id: str, quantity: int, timestamp: str):
        """
        Резервирование продукта.
        :param reservation_id: id резервации
        :param product_id: id продукта
        :param quantity: количество для резервирования
        :param timestamp: время резервирования
        :return: данные о созданной резервации или ошибку
        """
        data_product = await self.get_data_o_from_db(type_o='Product', id_o=product_id)
        await self.update_product_at_stock(data_product=data_product, quantity=quantity)
        return await self.add_reservation(reservation_id, product_id, quantity, 'какой-то статус')

    async def get_data_o_from_db(self, type_o: str, id_o: str):
        """
        Получает данные из базы данных по типу и айди объекта.
        :param type_o: тип объекта
        :param id_o: id объекта
        :return: данные об объекте
        """
        result = await self.session.execute(
            select(type_o).where(Product.product_id == id_o)
        )
        return result.scalars().first()

    async def check_quantity_product_at_stock(self,data_product, quantity):
        """
        Проверяет, достаточно ли количества товара на складе.
        :param data_product: данные о товаре
        :param quantity: колво-товаров, которое нужно зарезервировать
        :return: ничего либо ошибку если товара меньше чем нужно
        """
        if not data_product and data_product.quantity < quantity:
            raise HTTPException(status_code=400, detail="Недостаточно товара на складе.")

    async def update_product_at_stock(self, data_product, quantity):
        """
        Обновляет данные о продукте на складе.
        :param data_product: данные о продукте
        :param quantity: колво-товаров, которое нужно зарезервировать
        :return: ничего либо ошибку если товара меньше чем нужно
        """
        await self.check_quantity_product_at_stock(data_product=data_product, quantity=quantity)

        new_quantity = data_product.quantity - quantity
        await self.session.execute(
            update(Product)
            .where(Product.product_id == data_product.product_id)
            .values(quantity=new_quantity, updated_at=func.now())
        )


    async def add_reservation(self, reservation_id: str, product_id: str, quantity: int,
                              status: str = "success"):
        """
        Добавляет резервацию в базу данных.
        :param reservation_id: id резервации
        :param product_id: id товара
        :param quantity: количество товара для резервирования
        :param status: статус резервации(по умолчанию 'success')
        :return: информацию о резервации
        """
        insert_query = await self.db_manager.insert_reservation(table_name='reservations',
                                                                            fields = 'reservation_id, product_id, quantity, timestamp, status',
                                                                            type_o='Reservation')
        try:
            await self.db_manager.update(insert_query = insert_query ,
                                         instance = {"reservation_id": reservation_id,"product_id": product_id,
                                                     "quantity": quantity,"timestamp": datetime.now(),"status": status}
                                         )
            self.logger.info(f"Резервация '{reservation_id}' успешно добавлена.")
            return {"status": "success", "message": "Reservation completed successfully.",
                    "reservation_id": reservation_id}
        except SQLAlchemyError as e:
            self.logger.info(f"Ошибка при добавлении резервации: {e}")

    @async_session_decorator()
    async def get_reservation_status(self, reservation_id: str):
        """
        Возвращает статус резервации.
        :param reservation_id: id резервации
        :return: статус резервации
        """
        data_reservation = await self.get_data_o_from_db(type_o='Reservation', id_o=reservation_id)
        if not data_reservation:
            raise HTTPException(status_code=404, detail="Резервация не найдена.")

        return {"status": data_reservation.status}
