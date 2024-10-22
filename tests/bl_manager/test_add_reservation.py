import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError


from app.bl_manager import BLManager


@pytest.mark.asyncio
async def test_add_reservation_success():
    """Проверка успешного добавления резервации."""
    bl_manager = BLManager()
    mock_session = AsyncMock()  # Mock the database session
    reservation_id = 'res123'
    product_id = 'prod456'
    quantity = 10

    result = await bl_manager.add_reservation(reservation_id, product_id, quantity, mock_session)

    assert result['status'] == 'success'
    assert result['message'] == 'Резервация успешно добавлена.'
    assert result['reservation_id'] == reservation_id

    mock_session.add.assert_called_once()


