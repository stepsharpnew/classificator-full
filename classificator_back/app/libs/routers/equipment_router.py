from datetime import  timedelta, timezone, datetime
from fastapi import APIRouter, Cookie, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Body, Response, HTTPException
from app.libs.auth.auth_handler import Auth
from app.libs.handlers.equipment_handlers import *
from app.settings import Settings
from app.schemas.schema import EquipmentCreateSchema
from fastapi import Path
settings = Settings()

security = HTTPBearer()

equipment_router = APIRouter()


@equipment_router.get("/equipment")
async def equipment_get_router(search = None, equipmentType = None, department = None, year=None, type=None, limit=20, offset=0):
    return await get_equipments(search, equipmentType, department, year, type, limit, offset)

@equipment_router.get("/archive")
async def equipment_get_router(search = None, equipmentType = None, department = None, year=None, type=None, limit=20, offset=0):
    return await get_equipments(search, equipmentType, department, year, type, limit, offset, archive=True)

@equipment_router.post('/equipment')
async def equipment_create_router(equipment: EquipmentCreateSchema, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await create_equipment(equipment=equipment, user=response.data['user'])

@equipment_router.put('/equipment')
async def equipment_update_router(data: EquipmentUpdateDataSchema, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await equipment_update(data=data,  user=response.data['user'])


@equipment_router.delete('/equipment')
async def equipment_delete_router(id: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await equipment_delete(id=id, user=response.data['user'])


@equipment_router.get('/request')
async def equipment_requests_get(credentials: HTTPAuthorizationCredentials = Security(security)):
    return await get_requests()
@equipment_router.post("/request")
async def equipment_request_create_router(equipment_id, type, act=None, to_department=None, from_department=None, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await create_request(equipment_id, type, act, to_department, from_department, user=response.data['user'])

@equipment_router.post('/request/{id}/approved')
async def equipment_request_approve_router(id: str = Path(...), credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await request_status(id, status='approved', user=response.data['user'])
    
@equipment_router.post('/request/{id}/rejected')
async def equipment_request_reject_router(id: str = Path(...), credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await request_status(id, status='rejected', user=response.data['user'])

@equipment_router.delete("/request")
async def equipment_request_delete_router(id, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await delete_request(id, user=response.data['user'])



@equipment_router.get('/backup-equipment')
async def backup_equipment_router():
    equipment_data = await backup_data()
    return JSONResponse(content=equipment_data, media_type='application/json')
