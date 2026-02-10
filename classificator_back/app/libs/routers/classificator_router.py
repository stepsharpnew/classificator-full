from fastapi import APIRouter, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.libs.auth.auth_handler import Auth
from app.libs.handlers.classificator_handlers import create_classification, delete_classification, get_classification, update_classification, get_classification_leaf, get_classification_tree
from fastapi import Security
classificator_router = APIRouter()

security = HTTPBearer()

@classificator_router.get('/classification')
async def get_classification_router(path: str = None, credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return(await get_classification(path=path))

@classificator_router.get('/classification-leaf')
async def get_classification_router(path: str = None):
    return(await get_classification_leaf())

@classificator_router.get('/classification-with-equipment')
async def get_classification_with_equipment_router():
    return await get_classification_tree()


@classificator_router.post('/classification')
async def create_classificator_router(path: str, name: str):
    return await create_classification(path=path, name=name)


@classificator_router.put('/classification')
async def create_classificator_router(path: str, name: str):
    return await update_classification(path=path, name=name)
    

@classificator_router.delete('/classification')
async def delete_classificator_router(path: str):
    await delete_classification(path=path)