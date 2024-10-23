from unittest.mock import AsyncMock, patch, ANY
import pytest
from app.bl_manager import BLManager
from fastapi import HTTPException
from app.models import Reservation

class MockReservation:
    def __init__(self, status):
        self.status = status

@pytest.fixture(params=['asyncio'])
def aiolib(request):
    return request.param

@pytest.mark.asyncio
async def test_get_reservation_status_success(aiolib):
    """Тест успешного получения статуса резервации"""
    bl_manager_instance = BLManager()

    reservation_id = "res_123"
    mock_reservation_data = MockReservation(status="reserved")

    with patch.multiple(bl_manager_instance,
                        get_data_o_from_db=AsyncMock(return_value=mock_reservation_data)):
        result = await bl_manager_instance.get_reservation_status(reservation_id)
        assert result == {
            "status": "reserved",
            "message": "Reservation completed successfully.",
            "reservation_id": reservation_id
        }

        bl_manager_instance.get_data_o_from_db.assert_awaited_once_with(type_o='Reservation', id_o=reservation_id,
                                                                        session=ANY)

@pytest.mark.asyncio
async def test_get_reservation_status_not_found(aiolib):
    """Тест неуспешного получения статуса резервации (резервация не найдена)"""
    bl_manager_instance = BLManager()

    reservation_id = "res_124"

    with patch.multiple(bl_manager_instance,
                        get_data_o_from_db=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc_info:
            await bl_manager_instance.get_reservation_status(reservation_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Резервация не найдена."

        bl_manager_instance.get_data_o_from_db.assert_awaited_once_with(type_o='Reservation', id_o=reservation_id,
                                                                        session=ANY)