import pytest

from unittest.mock import AsyncMock, patch, ANY
from app.bl_manager import BLManager


@pytest.mark.asyncio
async def test_reserve_item_success():
    """Тест успешного резервирования продукта"""
    bl_manager_instance = BLManager()

    product_id = "prod_456"
    quantity = 2
    timestamp = "2024-10-22T12:00:00Z"
    mock_product_data = {"id": product_id, "stock": 5}

    with patch.object(bl_manager_instance,
                      'get_data_o_from_db', AsyncMock(return_value=mock_product_data)), \
            patch.object(bl_manager_instance, 'update_product_at_stock', AsyncMock()), \
            patch.object(bl_manager_instance, 'add_reservation', AsyncMock(return_value={"status": "success"})):
        result = await bl_manager_instance.reserve_item(product_id, quantity)
        assert result == {"status": "success"}

        bl_manager_instance.get_data_o_from_db.assert_awaited_once_with(type_o='Product', id_o=product_id, session=ANY)
        bl_manager_instance.update_product_at_stock.assert_awaited_once()
        bl_manager_instance.add_reservation.assert_awaited_once()


