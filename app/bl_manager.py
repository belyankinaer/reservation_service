from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, update, func, text
from fastapi import HTTPException

from app.models import Product, Reservation


class BLManager:

    #todo добавить проверку что резервицая с там айди уже есть
    #todo проверка что такого продукта нет

    async def reserve_item(self, reservation_id: str, product_id: str, quantity: int, timestamp: str):
        # [ ---
        DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5433/postgres"
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        # --- ]
        async with async_session() as session:
            async with session.begin():
                # [ ---
                result = await session.execute(
                    select(Product).where(Product.product_id == product_id)
                )
                product = result.scalars().first()  # Получаем первый результат
                #--- ]

                if not product or product.quantity < quantity:
                    raise HTTPException(status_code=400, detail="Недостаточно товара на складе.")

                #{"status": "error", "message": "Not enough stock available.", "reservation_id": "98765"}

                # [ ---
                new_quantity = product.quantity - quantity
                await session.execute(
                    update(Product)
                    .where(Product.product_id == product_id)
                    .values(quantity=new_quantity, updated_at=func.now())
                )
                # --- ]
            await session.commit()

            try:
                timestamp_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат временной метки.")

        return await self.add_reservation(reservation_id, product_id, quantity,
                                          'какой то статус')
        ...

    async def add_reservation(self, reservation_id: str, product_id: str, quantity: int,
                              status: str = "pending"):
        DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5433/postgres"
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        timestamp = datetime.now()

        insert_reservation_query = text("""
            INSERT INTO reservations (reservation_id, product_id, quantity, timestamp, status)
            VALUES (:reservation_id, :product_id, :quantity, :timestamp, :status)
            ON CONFLICT (reservation_id) DO UPDATE 
            SET product_id = EXCLUDED.product_id,
                quantity = EXCLUDED.quantity,
                timestamp = EXCLUDED.timestamp,
                status = EXCLUDED.status;
        """)

        try:
            async with async_session() as session:
                async with session.begin():


                    await session.execute(insert_reservation_query, {
                        "reservation_id": reservation_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "timestamp": timestamp,
                        "status": status
                    })
                print(f"Резервация '{reservation_id}' успешно добавлена.")
                return {"status": "success", "message": "Reservation completed successfully.",
                        "reservation_id": reservation_id}
        except SQLAlchemyError as e:
            print(f"Ошибка при добавлении резервации: {e}")

    async def get_reservation_status(self, reservation_id: str):
        DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5433/postgres"
        engine = create_async_engine(DATABASE_URL, echo=True)
        async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Reservation).where(Reservation.reservation_id == reservation_id)
                )
                reservation = result.scalars().first()

                if not reservation:
                    raise HTTPException(status_code=404, detail="Резервация не найдена.")

                return {"status": reservation.status}
