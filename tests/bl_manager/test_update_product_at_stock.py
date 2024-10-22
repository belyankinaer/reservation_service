from app.bl_manager import BLManager
from app.models import Product

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_update_product_at_stock_success():
    """Проверка на работу функции update_product_at_stock на успешное обновление товара"""
    bl_manager = BLManager()
    data_product = Product(product_id='123', name='Test Product', quantity=10)
    quantity_to_reserve = 5

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()

    try:
        await bl_manager.update_product_at_stock(data_product, quantity_to_reserve, mock_session)

        mock_session.execute.assert_called_once()
        call_args = mock_session.execute.call_args[0][0]
        assert call_args.__class__.__name__ == 'Update'

    except HTTPException as e:
        pytest.fail(f"Function raised an exception: {e.detail}")


@pytest.mark.asyncio
async def test_update_product_at_stock_not_enough_quantity():
    """Проверка на работу функции update_product_at_stock для недостаточного количества товара"""
    bl_manager = BLManager()
    data_product = Product(product_id='123', name='Test Product', quantity=2)
    quantity_to_reserve = 5

    mock_session = AsyncMock(spec=AsyncSession)

    with pytest.raises(HTTPException) as exc_info:
        await bl_manager.update_product_at_stock(data_product, quantity_to_reserve, mock_session)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Недостаточно товара на складе."