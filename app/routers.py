from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .bl_manager import BLManager
from .db_manager import get_db, SessionLocal

from pydantic import BaseModel


router = APIRouter()


class ReservationRequest(BaseModel):
    reservation_id: str
    product_id: str
    quantity: int
    timestamp: str

class ReservationStatusRequest(BaseModel):
    reservation_id: str

bl_manager = BLManager()

@router.post("/api/v1/reserve", response_model=dict)
#Метод для приема запросов на резервирование товаров
async def reserve_item_api(reservation_request: ReservationRequest):
    return await bl_manager.reserve_item(reservation_id = reservation_request.reservation_id,
                                   product_id = reservation_request.product_id,
                                   quantity = reservation_request.quantity,
                                   timestamp = reservation_request.timestamp)

# todo добавить Метод для получения статуса резервирования

@router.post("/api/v1/get_reservation_status/{reservation_id}", response_model=dict)
#Метод для приема запросов на резервирование товаров
async def get_reservation_status_api(reservation_request: ReservationStatusRequest):
    return await bl_manager.get_reservation_status(reservation_id = reservation_request.reservation_id)
