from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from uuid import UUID
from typing import Optional
from app.schemas.schema import EquipmentType

from app.libs.handlers.equipment_type_handlers import create_equipment_type, get_equipment_type, delete_equipment_type, \
     update_equipment_type, get_equipment_type_by_path

equipment_type_router = APIRouter()


@equipment_type_router.get('/equipment-type')
async def get_equipment_router(name: str = None):
    return await get_equipment_type(name=name)

# @equipment_type_router.get('/equipment-type/{path}')
# async def get_equipment_router(path: str):
#     return await get_equipment_type_by_path(path=path)



@equipment_type_router.post('/equipment-type')
async def create_equipment_router(path: str, name: str, type: Optional[str] = None, fnn: str = None):
    # Обрабатываем пустую строку как None

    type_value = None
    if type and type.strip():
        try:
            type_enum = EquipmentType(type)
            type_value = type_enum.value
        except ValueError:
            # Если значение не соответствует enum, оставляем None
            type_value = None
    return await create_equipment_type(classificator_path=path, name=name, type=type_value, fnn=fnn)
    

@equipment_type_router.delete('/equipment-type')
async def delete_equipment_router(id: UUID):
    return await delete_equipment_type(equipment_id=id)


@equipment_type_router.put('/equipment-type')
async def update_equipment_router(id: UUID, name: str, fnn: str):
    return await update_equipment_type(equipment_id=id, name=name, fnn=fnn)