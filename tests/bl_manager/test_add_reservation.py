import pytest
from unittest.mock import AsyncMock

from app.bl_manager import BLManager


@pytest.mark.asyncio
async def test_add_reservation_success():
    """Проверка успешного добавления резервации."""
    bl_manager = BLManager()
    mock_session = AsyncMock()
    product_id = 'prod456'
    quantity = 10
    result = await bl_manager.add_reservation(product_id, quantity, mock_session)

    assert result['status'] == 'success'
    assert result['message'] == 'Резервация успешно добавлена.'

    mock_session.add.assert_called_once()
