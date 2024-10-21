from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .bl_manager import BLManager
from .db_manager import SessionLocal

from pydantic import BaseModel

from .utils import ReservationRequest, ReservationStatusRequest

router = APIRouter()
bl_manager = BLManager()


@router.post("/api/v1/reserve", response_model=dict, description="Метод для резервирования товаров")
async def reserve_item_api(reservation_request: ReservationRequest):
    return await bl_manager.reserve_item(reservation_id=reservation_request.reservation_id,
                                         product_id=reservation_request.product_id,
                                         quantity=reservation_request.quantity,
                                         timestamp=reservation_request.timestamp)


@router.post("/api/v1/get_reservation_status/{reservation_id}", response_model=dict,
             description="Метод для получения статуса резервирования")
async def get_reservation_status_api(reservation_request: ReservationStatusRequest):
    return await bl_manager.get_reservation_status(reservation_id=reservation_request.reservation_id)
