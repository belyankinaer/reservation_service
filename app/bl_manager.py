import logging
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update, func
from fastapi import HTTPException

from app.db_manager import DatabaseManager
from app.logging_config import setup_logging
from app.models import Product, model_mapping, Reservation
from app.utils import async_session_decorator


class BLManager:

    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.session = AsyncSession()
        self.db_manager = DatabaseManager()


    @async_session_decorator()
    async def reserve_item(self, reservation_id: str, product_id: str, quantity: int, timestamp: str,
                           session: AsyncSession) -> dict:
        """
        Резервирование продукта.
        :param reservation_id: id резервации
        :param product_id: id продукта
        :param quantity: количество для резервирования
        :param timestamp: время резервирования
        :return: данные о созданной резервации или ошибку
        """
        data_product = await self.get_data_o_from_db(type_o='Product', id_o=product_id, session=session)
        await self.update_product_at_stock(data_product=data_product, quantity=quantity, session=session)
        return await self.add_reservation(reservation_id, product_id, quantity, session)


    async def get_data_o_from_db(self, type_o: str, id_o: str, session) -> object:
        """
        Получает данные из базы данных по типу и айди объекта.
        :param type_o: тип объекта
        :param id_o: id объекта
        :return: данные об объекте
        """
        try:
            if type_o not in model_mapping.keys():
                raise ValueError(f"Неизвестный тип объекта '{type_o}'")
            elif type_o == 'Product':
                result = await session.execute(
                    select(Product).where(Product.product_id == id_o)
                )
                return result.scalars().first()
            elif type_o == 'Reservation':
                result = await session.execute(
                    select(Reservation).where(Reservation.reservation_id == id_o)
                )
            return result.scalars().first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting data from database: {e}")


    @staticmethod
    async def check_quantity_product_at_stock(data_product: Product, quantity: int):
        """
        Проверяет, достаточно ли количества товара на складе.
        :param data_product: данные о товаре
        :param quantity: колво-товаров, которое нужно зарезервировать
        :return: ничего либо ошибку если товара меньше чем нужно
        """
        if not data_product or data_product.quantity < quantity:
            raise HTTPException(status_code=400, detail="Недостаточно товара на складе.")

    async def update_product_at_stock(self, data_product: Product, quantity: int, session: AsyncSession):
        """
        Обновляет данные о продукте на складе.
        :param data_product: данные о продукте
        :param quantity: количество товаров, которое нужно зарезервировать
        :return: ничего либо ошибку если товара меньше чем нужно
        """
        await self.check_quantity_product_at_stock(data_product=data_product, quantity=quantity)
        new_quantity = data_product.quantity - quantity

        await session.execute(
            update(Product)
            .where(Product.product_id == data_product.product_id)
            .values(quantity=new_quantity, updated_at=func.now())
        )


    async def add_reservation(self, reservation_id: str, product_id: str, quantity: int, session) -> dict:
        """
        Добавляет резервацию в базу данных.
        :param reservation_id: id резервации
        :param product_id: id товара
        :param quantity: количество товара для резервирования
        :param status: статус резервации(по умолчанию 'success')
        :return: информацию о резервации
        """
        new_reservation = Reservation(reservation_id=reservation_id, product_id=product_id, quantity=quantity,
                                      timestamp=datetime.now(), status='success')
        try:
            session.add(new_reservation)
            self.logger.info(f"Резервация '{reservation_id}' успешно добавлена.")
            return {"status": "success", "message": "Резервация успешно добавлена.",
                    "reservation_id": reservation_id}
        except SQLAlchemyError as e:
            self.logger.info(f"Ошибка при добавлении резервации: {e}")
            raise SQLAlchemyError(f"Ошибка при добавлении резервации: {e}")

    @async_session_decorator()
    async def get_reservation_status(self, reservation_id: str, session: AsyncSession) -> dict:
        """
        Возвращает статус резервации.
        :param reservation_id: id резервации
        :return: статус резервации
        """
        data_reservation = await self.get_data_o_from_db(type_o='Reservation', id_o=reservation_id, session=session)
        if not data_reservation:
            raise HTTPException(status_code=404, detail="Резервация не найдена.")

        return {"status": data_reservation.status,
                "message": "Reservation completed successfully.",
                "reservation_id": reservation_id}
