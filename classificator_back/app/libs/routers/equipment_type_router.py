from fastapi import APIRouter, Request, HTTPException, Security
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID
from typing import Optional
from app.schemas.schema import EquipmentType, Response
from app.libs.auth.auth_handler import Auth

from app.libs.handlers.equipment_type_handlers import create_equipment_type, get_equipment_type, delete_equipment_type, \
     update_equipment_type, get_equipment_type_by_path

equipment_type_router = APIRouter()
security = HTTPBearer()


def _can_edit_equipment_type(user: dict) -> bool:
    if not user:
        return False
    return user.get('role') == 'chief_engineer' or user.get('is_superuser') is True


@equipment_type_router.get('/equipment-type')
async def get_equipment_router(name: str = None):
    return await get_equipment_type(name=name)


@equipment_type_router.post('/equipment-type')
async def create_equipment_router(path: str, name: str, type: Optional[str] = None, fnn: str = None, staff_number: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    if not _can_edit_equipment_type(response.data.get('user')):
        raise HTTPException(status_code=403, detail='Редактирование типов оборудования доступно только главному инженеру')
    type_value = None
    if type and type.strip():
        try:
            type_enum = EquipmentType(type)
            type_value = type_enum.value
        except ValueError:
            type_value = None
    success, error = await create_equipment_type(classificator_path=path, name=name, type=type_value, fnn=fnn, staff_number=staff_number)
    if not success:
        return Response(data=None, success=False, error={'msg': error})
    return Response(data='Тип оборудования создан', success=True, error=None)


@equipment_type_router.delete('/equipment-type')
async def delete_equipment_router(id: UUID, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    if not _can_edit_equipment_type(response.data.get('user')):
        raise HTTPException(status_code=403, detail='Редактирование типов оборудования доступно только главному инженеру')
    success, error = await delete_equipment_type(equipment_id=id)
    if not success:
        return Response(data=None, success=False, error={'msg': error})
    return Response(data='Тип оборудования удалён', success=True, error=None)


@equipment_type_router.put('/equipment-type')
async def update_equipment_router(id: UUID, name: str, fnn: str, type: Optional[str] = None, staff_number: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    if not _can_edit_equipment_type(response.data.get('user')):
        raise HTTPException(status_code=403, detail='Редактирование типов оборудования доступно только главному инженеру')
    type_value = None
    if type and type.strip():
        try:
            type_enum = EquipmentType(type)
            type_value = type_enum.value
        except ValueError:
            type_value = None
    success, error = await update_equipment_type(equipment_id=id, name=name, fnn=fnn, type=type_value, staff_number=staff_number)
    if not success:
        return Response(data=None, success=False, error={'msg': error})
    return Response(data='Тип оборудования обновлён', success=True, error=None)