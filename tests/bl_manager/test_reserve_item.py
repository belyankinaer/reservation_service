import pytest

from unittest.mock import AsyncMock, patch, ANY
from app.bl_manager import BLManager


@pytest.fixture(params=['asyncio'])
def aiolib(request):
    return request.param


@pytest.mark.asyncio
async def test_reserve_item_success(aiolib):
    """Тест успешного резервирования продукта"""
    bl_manager_instance = BLManager()

    reservation_id = "res_123"
    product_id = "prod_456"
    quantity = 2
    timestamp = "2024-10-22T12:00:00Z"
    mock_product_data = {"id": product_id, "stock": 5}

    with patch.multiple(bl_manager_instance,
                        get_data_o_from_db=AsyncMock(return_value=mock_product_data),
                        update_product_at_stock=AsyncMock(),
                        add_reservation=AsyncMock(return_value={"status": "success", "reservation_id": reservation_id})):

        result = await bl_manager_instance.reserve_item(reservation_id, product_id, quantity, timestamp)
        assert result == {"status": "success", "reservation_id": reservation_id}

        bl_manager_instance.get_data_o_from_db.assert_awaited_once_with(type_o='Product', id_o=product_id, session=ANY)
        bl_manager_instance.update_product_at_stock.assert_awaited_once()
        bl_manager_instance.add_reservation.assert_awaited_once_with(reservation_id, product_id, quantity, ANY)


@pytest.mark.asyncio
async def test_reserve_item_failure(aiolib):
    """Тест ошибочного резервирования продукта"""
    bl_manager_instance = BLManager()

    reservation_id = "res_124"
    product_id = "prod_457"
    quantity = 1
    timestamp = "2024-10-22T12:00:00Z"

    with patch.multiple(bl_manager_instance,
                        get_data_o_from_db=AsyncMock(side_effect=Exception("Database error")),
                        update_product_at_stock=AsyncMock(),
                        add_reservation=AsyncMock()):

        with pytest.raises(Exception) as exc_info:
            await bl_manager_instance.reserve_item(reservation_id, product_id, quantity, timestamp)
        assert str(exc_info.value) == "Database error"

        bl_manager_instance.get_data_o_from_db.assert_awaited_once_with(type_o='Product', id_o=product_id, session=ANY)
        bl_manager_instance.update_product_at_stock.assert_not_awaited()  # Не должен быть вызван при ошибке
        bl_manager_instance.add_reservation.assert_not_awaited()  # Не должен быть вызван при ошибке


