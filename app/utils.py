from pydantic import BaseModel
import functools
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.constants import DATABASE_URL


class ReservationRequest(BaseModel):
    """ Модель запроса резервирования """
    reservation_id: str
    product_id: str
    quantity: int
    timestamp: str


class ReservationStatusRequest(BaseModel):
    """ Модель запроса статуса резервирования """
    reservation_id: str


def async_session_decorator():
    """Декоратор для управления асинхронной сессией SQLAlchemy."""

    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with async_session_maker() as session:
                async with session.begin():
                    try:
                        result = await func(*args, session=session, **kwargs)
                        await session.commit()
                        return result
                    except Exception as e:
                        await session.rollback()
                        raise e

        return wrapper

    return decorator