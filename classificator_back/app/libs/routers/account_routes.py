from datetime import  timedelta, timezone, datetime
from fastapi import APIRouter, Cookie, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Body, Response, HTTPException
from app.libs.auth.auth_handler import Auth
from app.libs.handlers.registration_handler import *
from app.settings import Settings

settings = Settings()

security = HTTPBearer()

account_router = APIRouter()


@account_router.post("/login")
async def login_route(login: str, password: str = Body(embed=True)):
    data = await login_handler(login, password)

    response = JSONResponse(content=data.dict())
    if data.data:
        response.set_cookie(
            key="refresh_token",
            value=data.data.get("refresh_token"),
            secure=False, #разрешает передачу куки через http, запрещает если True
            httponly=True,
            expires=datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_refresh_token_expires_in),
        )
    return response


@account_router.post("/refresh")
async def refresh_route(refresh_token=Cookie()):
    response = await Auth.decode_refresh_token(refresh_token)
    if not response.success:
        raise HTTPException(status_code=401, detail=response.error.get('msg'))
    data = await update_refresh_token(refresh_token)
    if not data.success:
        print('12312312')
        raise HTTPException(status_code=401, detail=data.error.get('msg'))
    response = JSONResponse(content=data.dict())
    if data.data:
        response.set_cookie(
            key="refresh_token", value=data.data.get("refresh_token"), httponly=True
        )
    return response


@account_router.post("/logout")
async def logout_route(response: JSONResponse, refresh_token=Cookie()):
    response.delete_cookie(key='refresh_token')
    return await delete_refresh_token(refresh_token)





@account_router.post("/user")
async def create_user_route(
    user: UsersRegisterSchema,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    return await create_account(credentials=credentials, user=user)

@account_router.put("/password")
async def create_user_route(
    login: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
    new_password = Body(),
):
    return await change_password_by_admin(credentials=credentials, login=login, new_password=new_password)


@account_router.get('/users')
async def get_users_route(department: str = None):
    return await get_users(department)


@account_router.get("/departments")
async def get_departments_route():
    return await get_departments()




@account_router.post("/department")
async def create_department_route(
    name: str,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    return await create_department(credentials=credentials, name=name)





# @account_router.post("/password/change")
# async def change_password_route(
#     new_password: str = Body(embed=True),
#     credentials: HTTPAuthorizationCredentials = Security(security),
# ):
#     return await change_password(credentials, new_password)
