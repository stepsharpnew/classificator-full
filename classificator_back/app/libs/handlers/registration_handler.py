import os
import secrets
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from app.settings import get_settings
from sqlalchemy.orm import selectinload
from app.libs.postgres.models import *
from app.schemas.schema import *

from app.libs.auth.auth_handler import Auth

from app.schemas.schema import Response
from fastapi import HTTPException
settings = get_settings()
async_session = settings.async_session



async def login_handler(login: str, password: str) -> Response:
    async with async_session() as session:
        stmt = select(Users).where(Users.login == login)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if not user:
           raise HTTPException(status_code=403, detail=f"Пользователь с указанным логином не существует")
        if not await Auth.verify_password(password, user.password):
            raise HTTPException(status_code=403, detail=f"Неверный пароль")
        if user.department_id is None:
            department = 'admin'
        else:
            department = str(user.department_id)
        _user = UsersResponseSchema(id=str(user.id),
                                    login=user.login,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    department_id=department,
                                    role=user.role,
                                    is_superuser=user.is_superuser
                                    )
        access_token = await Auth.get_access_token(_user.dict())
        refresh_token = await Auth.get_refresh_token(_user.dict())
        stmt = insert(RefreshTokens).values(user_id=user.id, refresh_token=refresh_token)
        stmt = stmt.on_conflict_do_update(constraint='refresh_tokens_pkey',
                                          set_={'refresh_token': refresh_token})

        await session.execute(stmt)
        await session.commit()

        return Response(data={'access_token': access_token,
                              'refresh_token': refresh_token,
                              'user': _user.dict()},
                        success=True,
                        error=None)

async def update_refresh_token(token: str) -> Response:
    response = await Auth.decode_refresh_token(token)
    print(response)
    user_id = response.data.get('user').get('id')
    print(user_id)
    async with async_session() as session:
        stmt = select(Users).where(Users.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        print(user)
        if not user:
            raise HTTPException(status_code=403, detail=f"Пользователь с указанным логином не существует")
        stmt = select(RefreshTokens).where(RefreshTokens.user_id == user.id)
        result = await session.execute(stmt)
        rt = result.scalars().first()
        if not rt:
            raise HTTPException(status_code=403, detail=f"Токен не существует")
        if rt.refresh_token == token:
            if user.department_id is None:
                department = 'admin'
            else:
                department = str(user.department_id)
            _user = UsersResponseSchema(id=str(user.id),
                                        login=user.login,
                                        first_name=user.first_name,
                                        last_name=user.last_name,
                                        department_id=department,
                                        role=user.role,
                                        is_superuser=user.is_superuser
                                        )
            access_token = await Auth.get_access_token(_user.dict())
            refresh_token = await Auth.get_refresh_token(_user.dict())
            stmt = insert(RefreshTokens).values(user_id=user.id, refresh_token=refresh_token)
            stmt = stmt.on_conflict_do_update(constraint='refresh_tokens_pkey',
                                              set_={'refresh_token': refresh_token})
            try:
                await session.execute(stmt)
                await session.commit()
            except Exception as exc:
                raise HTTPException(status_code=404, detail=f"Ошибка {exc}")
            return Response(data={'access_token': access_token,
                                  'refresh_token': refresh_token,
                                  'user': _user.dict()},
                            error=None,
                            success=True)
        else:
            raise HTTPException(status_code=403, detail=f"Токен не существует")


async def delete_refresh_token(token: str) -> Response:
    response = await Auth.decode_refresh_token(token)
    if not response.success:
        return response
    user_id = response.data.get('user').get('id')
    async with async_session() as session:
        stmt = select(Users).where(Users.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if not user:
            return Response(error={'code': 10016,
                                   'msg': 'Пользователь не существует'},
                            success=False)
        stmt = select(RefreshTokens).where(RefreshTokens.user_id == user.id)
        result = await session.execute(stmt)
        rt = result.scalars().first()
        if not rt:
            return Response(error={'code': 10008,
                                   'msg': 'Токена не существует'},
                            success=False)
        stmt = delete(RefreshTokens).where(RefreshTokens.user_id == rt.user_id)
        await session.execute(stmt)
        await session.commit()
        return Response(success=True, data=None, error=None)
    
    
    
    
    
async def create_account(credentials, user):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        return response
    if not response.data.get('user').get('is_superuser'):
        raise HTTPException(status_code=403, detail=f"Недостаточно прав")

    async with async_session() as session:
        stmt = select(Users).where(Users.login == user.login)
        result = await session.execute(stmt)
        _user = result.scalars().first()
        if _user:
            raise HTTPException(status_code=404, detail=f"Пользователь с указанным логином уже существует")

        stmt = select(Users).where(Users.department_id == user.department_id)
        result = await session.execute(stmt)
        users = result.scalars().all()

    

        for _user in users:
            if _user.role == 'mol':
                raise HTTPException(status_code=404, detail=f"МОЛ для этого подразделения уже существует")

                

        
        password = await Auth.encode_password(user.password)
        new_user = Users(login=user.login, 
                         first_name=user.first_name,
                         last_name=user.last_name,
                         role=user.role,
                         department_id=user.department_id,
                         password=password
                         )
        session.add(new_user)
        await session.commit()
        return new_user

async def create_department(credentials, name):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        return response
    if not response.data.get('user').get('is_superuser'):
        raise HTTPException(status_code=403, detail=f"Недостаточно прав")
    async with async_session() as session:
        stmt = select(Department).where(Department.name == name)
        result = await session.execute(stmt)
        _department = result.scalars().first()
        if _department:
            raise HTTPException(status_code=404, detail=f"Подразделение с таким названием уже существует")
        department = Department(name=name
                         )
        session.add(department)
        await session.commit()
        return department

async def get_departments():
    async with async_session() as session:
        stmt = select(Department).options(selectinload(Department.users))
        result = await session.execute(stmt)
        departments = result.scalars().all()
        return departments


async def get_users(department:str = None):
  async with async_session() as session:
    if department:
        stmt = select(Department).where(Department.name == department)
        result = await session.execute(stmt)
        _department = result.scalars().first()
        if not _department:
             raise HTTPException(status_code=404, detail=f"Указанное подразделение не сущестувет")
        stmt = select(Users).where(Users.department_id == _department.id).options(
        selectinload(Users.department))
        result = await session.execute(stmt)
        users = result.scalars().all()
    else:
        stmt = select(Users).options(
        selectinload(Users.department))
        result = await session.execute(stmt)
        users = result.scalars().all()
    return users
    



async def change_password_by_admin(login, new_password, credentials):
    response = await Auth.decode_access_token(credentials.credentials)
    if not response.success:
        return response
    if not response.data.get('user').get('is_superuser'):
        raise HTTPException(status_code=403, detail=f"Недостаточно прав")

    async with async_session() as session:
        # Находим пользователя по ID
        stmt = select(Users).where(Users.login == login)
        result = await session.execute(stmt)
        user_to_update = result.scalars().first()

        if not user_to_update:
            raise HTTPException(status_code=404, detail="Пользователь с указанным login не найден")

        try:
            # Хэшируем новый пароль
            hashed_password = await Auth.encode_password(new_password)

            # Обновляем пароль пользователя
            user_to_update.password = hashed_password

            # Сохраняем изменения в базе данных
            session.add(user_to_update)
            await session.commit()

            return user_to_update
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при выполнении операции в базе данных: {str(e)}")