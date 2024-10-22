import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.bl_manager import BLManager
from app.models import Product


@pytest.mark.asyncio
async def test_check_quantity_product_at_stock_no_error():
    """Проверка на работу функции check_quantity_product_at_stock для достаточного количества товара"""
    bl_manager = BLManager()

    data_product = Product(product_id='123', name='Test Product', quantity=10)
    quantity_to_reserve = 5

    try:
        await bl_manager.check_quantity_product_at_stock(data_product, quantity_to_reserve)
    except HTTPException as e:
        pytest.fail(f"Function raised an exception: {e.detail}")

@pytest.mark.asyncio
async def test_check_quantity_product_at_stock_not_enough_quantity():
    """Проверка на работу функции check_quantity_product_at_stock для недостаточного количества товара"""
    bl_manager = BLManager()

    data_product = Product(product_id='123', name='Test Product', quantity=2)
    quantity_to_reserve = 5

    with pytest.raises(HTTPException) as exc_info:
        await bl_manager.check_quantity_product_at_stock(data_product, quantity_to_reserve)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Недостаточно товара на складе."