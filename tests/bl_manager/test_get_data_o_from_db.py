import pytest

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.bl_manager import BLManager, Product, Reservation

model_mapping = {
    'Product': Product,
    'Reservation': Reservation,
}


@pytest.mark.asyncio
async def test_get_data_o_from_db_product_no_error():
    """Проверка на работу функции get_data_o_from_db для товара без ошибок"""
    bl_manager = BLManager()

    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = Product(product_id='123', name='Test Product')

    mock_session.execute.return_value = mock_result

    try:
        result = await bl_manager.get_data_o_from_db('Product', '123', mock_session)
        assert result.product_id == '123'
    except Exception as e:
        pytest.fail(f"Function raised an exception: {e}")


@pytest.mark.asyncio
async def test_get_data_o_from_db_reservation_no_error():
    """Проверка на работу функции get_data_o_from_db для резервации без ошибок"""
    bl_manager = BLManager()

    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = Reservation(reservation_id='456')
    mock_session.execute.return_value = mock_result

    try:
        result = await bl_manager.get_data_o_from_db('Reservation', '456', mock_session)
        assert result.reservation_id == '456'
    except Exception as e:
        pytest.fail(f"Function raised an exception: {e}")


@pytest.mark.asyncio
async def test_get_data_o_from_db_invalid_type():
    """Проверка на работу функции get_data_o_from_db для некорректного типа объекта"""
    bl_manager = BLManager()

    mock_session = AsyncMock(spec=AsyncSession)

    with pytest.raises(ValueError, match="Неизвестный тип объекта"):
        await bl_manager.get_data_o_from_db('UnknownType', '123', mock_session)
