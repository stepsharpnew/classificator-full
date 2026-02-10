from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas.schema import NoteCreateSchema, NoteUpdateSchema, NoteSearchSchema
from app.libs.auth.auth_handler import Auth
from app.libs.handlers.notes_handlers import *
from fastapi import Security
from typing import Optional


security = HTTPBearer()

notes_router = APIRouter()

@notes_router.get("/notes")
async def notes_get_router(
    search: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    
    # Преобразуем строку тегов в список
    tag_list = tags.split(',') if tags else None
    
    search_data = NoteSearchSchema(
        query=search,
        tags=tag_list,
        limit=limit,
        offset=offset
    )
    
    return await get_notes(search_data)

@notes_router.post('/notes')
async def notes_create_router(
    note: NoteCreateSchema,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await create_note(note=note, user=response.data['user'])

@notes_router.put('/notes/{note_id}')
async def notes_update_router(
    note_id: str,
    note: NoteUpdateSchema,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await update_note(note_id=note_id, note_data=note, user=response.data['user'])

@notes_router.delete('/notes/{note_id}')
async def notes_delete_router(
    note_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await delete_note(note_id=note_id, user=response.data['user'])

@notes_router.get('/tags')
async def tags_get_router(credentials: HTTPAuthorizationCredentials = Security(security)):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await get_tags()

@notes_router.put('/tags/{tag_id}')
async def tags_update_router(
    tag_id: str,
    tag_data: TagCreate,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await update_tag(tag_id=tag_id, tag_data=tag_data, user=response.data['user'])

@notes_router.delete('/tags/{tag_id}')
async def tags_delete_router(
    tag_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    return await delete_tag(tag_id=tag_id, user=response.data['user'])