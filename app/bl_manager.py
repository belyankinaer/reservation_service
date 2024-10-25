import logging
import uuid
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update, func
from fastapi import HTTPException

from app.logging_config import setup_logging
from app.models import Product, model_mapping, Reservation
from app.utils import async_session_decorator


class BLManager:
    """Класс BLManager отвечает за управление бизнес-логикой резервирования товаров.

    Этот класс предоставляет методы для резервирования товаров, проверки статуса резерваций и взаимодействия с базой данных.
    Он использует SQLAlchemy для асинхронного доступа к базе данных и включает в себя обработку ошибок и ведение логов.

    Атрибуты:
        logger (logging.Logger): Логгер для записи информации и ошибок.
        session (AsyncSession): Асинхронная сессия для работы с базой данных."""

    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.session = AsyncSession()

    @async_session_decorator()
    async def reserve_item(self, product_id: str, quantity: int, session: AsyncSession) -> dict:
        """
        Резервирование продукта.
        :param product_id: id продукта
        :param quantity: количество для резервирования
        :param session: данные сессии
        :return: данные о созданной резервации
        """
        data_product = await self.get_data_o_from_db(type_o='Product', id_o=product_id, session=session)
        await self.update_product_at_stock(data_product=data_product, quantity=quantity, session=session)
        return await self.add_reservation(product_id=product_id, quantity=quantity, session=session)

    async def get_data_o_from_db(self, type_o: str, id_o: str, session) -> object:
        """
        Получает данные из базы данных по типу и айди объекта.
        :param type_o: тип объекта
        :param id_o: id объекта
        :param session: данные сессии
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
            self.logger.error("Ошибка получения данных из базы данных: %s", e)

    @staticmethod
    async def check_quantity_product_at_stock(data_product: Product, quantity: int):
        """
        Проверяет, достаточно ли количества товара на складе.
        :param data_product: данные о товаре
        :param quantity: количество товаров, которое нужно зарезервировать
        :return: ничего либо ошибку если товара меньше чем нужно
        """
        if not data_product or data_product.quantity < quantity:
            raise HTTPException(status_code=400,
                                detail=f"Недостаточно товара на складе.Количество остатка: {data_product.quantity}")

    async def update_product_at_stock(self, data_product: object, quantity: int, session: AsyncSession):
        """
        Обновляет данные о продукте на складе.
        :param data_product: данные о продукте
        :param quantity: количество товаров, которое нужно зарезервировать
        :param session: данные сессии
        :return: ничего либо ошибку если товара меньше чем нужно
        """
        await self.check_quantity_product_at_stock(data_product=data_product, quantity=quantity)
        new_quantity = data_product.quantity - quantity

        await session.execute(
            update(Product)
            .where(Product.product_id == data_product.product_id)
            .values(quantity=new_quantity, updated_at=func.now())
        )

    async def add_reservation(self, product_id: str, quantity: int, session) -> dict:
        """
        Добавляет резервацию в базу данных.
        :param product_id: id товара
        :param quantity: количество товара для резервирования
        :param status: статус резервации(по умолчанию 'success')
        :param session: данные сессии
        :return: информацию о резервации
        """
        reservation_id = str(uuid.uuid4())
        new_reservation = Reservation(reservation_id=reservation_id, product_id=product_id, quantity=quantity,
                                      timestamp=datetime.now(), status='success')
        try:
            session.add(new_reservation)
            self.logger.info("Резервация %s успешно добавлена.", reservation_id)
            return {"reservation_id": reservation_id,"status": "success", "message": "Резервация успешно добавлена."}
        except SQLAlchemyError as e:
            self.logger.info("Ошибка при добавлении резервации: %s", e)
            raise SQLAlchemyError(f"Ошибка при добавлении резервации: {e}")

    @async_session_decorator()
    async def get_reservation_status(self, reservation_id: str, session: AsyncSession) -> dict:
        """
        Возвращает статус резервации.
        :param reservation_id: id резервации
        :param session: данные сессии
        :return: статус резервации
        """
        data_reservation = await self.get_data_o_from_db(type_o='Reservation', id_o=reservation_id, session=session)
        if not data_reservation:
            raise HTTPException(status_code=404, detail="Резервация не найдена. Проверьте правильность айди.")

        return {"status": data_reservation.status,
                "message": "Бронирование успешно завершено.",
                "reservation_id": reservation_id}
