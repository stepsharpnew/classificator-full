import os
import secrets
from datetime import datetime
from sqlalchemy import select, update, delete, extract
from sqlalchemy.dialects.postgresql import insert
from app.settings import get_settings
from sqlalchemy.orm import selectinload, joinedload
from app.libs.postgres.models import *
from app.schemas.schema import Response, EquipmentCreateSchema, EquipmentUpdateDataSchema
from app.libs.auth.auth_handler import Auth
from sqlalchemy import select, and_, or_, exists, not_
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func 
from app.schemas.schema import Response, EquipmentResponseSchema
from fastapi import HTTPException
from sqlalchemy.orm import joinedload, aliased
import json
settings = get_settings()
async_session = settings.async_session


def escape_search_string(search_string):
    if search_string:
        # Заменяем специальные символы на экранированные версии
        special_chars = ['-', '/', '+', '%', '_']
        for char in special_chars:
            search_string = search_string.replace(char, f'\\{char}')
    return search_string


async def get_equipments(search, equipmentType, department, year, type, limit=10, offset=0, archive=False):
    import time

    start_time = time.time()

    async with async_session() as session:
        if not archive:

            stmt = select(Equipment).options(
            joinedload(Equipment.eq_type), # joinedload для  EqType
            joinedload(Equipment.department), # joinedload для  Department
            joinedload(Equipment.components).joinedload(Equipment.eq_type),
            joinedload(Equipment.components).joinedload(Equipment.department),  # Загружаем components через JOIN
        ).where(and_(Equipment.status != 'archive', Equipment.status != 'transfered'))
        else:

            stmt = select(Equipment).options(
            joinedload(Equipment.eq_type), # joinedload для  EqType
            joinedload(Equipment.department), # joinedload для  Department
            joinedload(Equipment.components).joinedload(Equipment.eq_type),
            joinedload(Equipment.components).joinedload(Equipment.department),   # Загружаем components через JOIN
        ).where(or_(Equipment.status == 'archive', Equipment.status == 'transfered'))
        
        not_a_child = not_(exists().where(equipment_components.c.component_id == Equipment.id))
        stmt = stmt.where(not_a_child)  # Добавляем условие к основному запросу

        if not archive:
            if search:
                search = escape_search_string(search) 
                search_pattern = f"%{search}%"
                # Условия поиска в родительском элементе
                parent_conditions = [
                    func.lower(Equipment.inventory_number).like(func.lower(search_pattern)),
                    func.lower(Equipment.factory_number).like(func.lower(search_pattern)),
                    func.lower(Equipment.act_of_receiving).like(func.lower(search_pattern)),
                    func.lower(Equipment.comment).like(func.lower(search_pattern)),
                   
                ]
                eq_type_fnn_condition = Equipment.eq_type.has(
                        func.lower(EquipmentType.fnn).like(func.lower(search_pattern))
                    )
                parent_conditions.append(eq_type_fnn_condition)

                child_exists = exists().where(
                and_(
                    equipment_components.c.parent_id == Equipment.id, # Связь через таблицу ассоциаций (родитель)
                    Equipment.components.any(  # Теперь используем relationship components
                        or_(
                            func.lower(Equipment.inventory_number).like(func.lower(search_pattern)),
                            func.lower(Equipment.factory_number).like(func.lower(search_pattern)),
                            func.lower(Equipment.act_of_receiving).like(func.lower(search_pattern)),
                            func.lower(Equipment.comment).like(func.lower(search_pattern)),
                            Equipment.eq_type.has(
                                func.lower(EquipmentType.fnn).like(func.lower(search_pattern))
                            )
                        )
                    )
                )
            ).correlate(Equipment)

                # Объединяем условия поиска: или в родительском элементе, или существует подходящий дочерний элемент
                stmt = stmt.where(or_(*parent_conditions, child_exists))
        else:
            if search:
                search = escape_search_string(search) 
                search_pattern = f"%{search}%"
                # Условия поиска в родительском элементе
                parent_conditions = [
                    func.lower(Equipment.inventory_number).like(func.lower(search_pattern)),
                    func.lower(Equipment.factory_number).like(func.lower(search_pattern)),
                    func.lower(Equipment.act_of_receiving).like(func.lower(search_pattern)),
                    func.lower(Equipment.act_of_decommissioning).like(func.lower(search_pattern)),
                    func.lower(Equipment.transfer_department).like(func.lower(search_pattern)),
                    func.lower(Equipment.comment).like(func.lower(search_pattern)),
                    
                ]

                # Ищем в дочерних элементах (через подзапрос EXISTS и таблицу ассоциаций)
                child_exists = exists().where(
                and_(
                    equipment_components.c.parent_id == Equipment.id, # Связь через таблицу ассоциаций (родитель)
                    Equipment.components.any(  # Теперь используем relationship components
                        or_(
                            func.lower(Equipment.inventory_number).like(func.lower(search_pattern)),
                            func.lower(Equipment.factory_number).like(func.lower(search_pattern)),
                            func.lower(Equipment.act_of_receiving).like(func.lower(search_pattern)),
                            func.lower(Equipment.comment).like(func.lower(search_pattern)),
                            
                        )
                    )
                )
            ).correlate(Equipment)

                # Объединяем условия поиска: или в родительском элементе, или существует подходящий дочерний элемент
                stmt = stmt.where(or_(*parent_conditions, child_exists))

                

        if equipmentType:
            parent_condition = Equipment.type == equipmentType
            child_exists = exists().where(
                and_(
                    equipment_components.c.parent_id == Equipment.id,
                    Equipment.components.any(Equipment.type == equipmentType)
                )
            ).correlate(Equipment)
            stmt = stmt.where(or_(parent_condition, child_exists))

        if type:
            if type == 'empty':
                # Только оборудование с пустым типом (eq_type.type IS NULL)
                parent_condition = Equipment.eq_type.has(EquipmentType.type.is_(None))
                child_condition = Equipment.components.any(Equipment.eq_type.has(EquipmentType.type.is_(None)))
                stmt = stmt.where(or_(parent_condition, child_condition))
            else:
                # Условие для родительского элемента
                parent_condition = Equipment.eq_type.has(type=type)
                # Условие для дочернего элемента (через any())
                child_condition = Equipment.components.any(Equipment.eq_type.has(type=type))
                stmt = stmt.where(or_(parent_condition, child_condition))
        
        if department:
            stmt = stmt.where(Equipment.department_id == department)

        if year:
            year = int(year)
            stmt = stmt.where(extract('year', Equipment.receiving_date) == year)

        count_stmt = select(func.count()).select_from(stmt.subquery())  # Важно subquery()
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar()
        stmt = stmt.order_by(Equipment.created_at)
        stmt = stmt.limit(limit).offset(offset)

        result = await session.execute(stmt)
        equipments = result.unique().scalars().all()

        end_time = time.time()

        elapsed_time = end_time - start_time
        print('\n')
        print(f"The task took {elapsed_time:.2f} seconds to complete.")
        print('\n')
        return {'equipments': equipments, 'total_count': total_count}
    
async def get_archive_equipments(search, equipmentType, department, year, type, limit=10, offset=0):
    async with async_session() as session:

        stmt = select(Equipment).where(or_(Equipment.status == 'archive', Equipment.status == 'transfered')).options(
            selectinload(Equipment.components).subqueryload(Equipment.department), # Загружаем department для компонентов
            selectinload(Equipment.components).subqueryload(Equipment.eq_type),     # Загружаем eq_type для компонентов
            selectinload(Equipment.department),
            selectinload(Equipment.eq_type),
        )
        result = await session.execute(stmt)
        equipments = result.scalars().all()
        return equipments
    

async def create_equipment(equipment: EquipmentCreateSchema, user):
    user_dept = user.get('department_id')
    role = (user.get('role') or '')
    role_str = str(role).strip().lower() if role else ''
    is_superuser = user.get('is_superuser') in (True, 'true', 1)
    can_any_department = is_superuser or role_str == 'chief_engineer'
    if user_dept is not None and not can_any_department:
        if str(equipment.department_id) != str(user_dept):
            raise HTTPException(
                status_code=400,
                detail='Нельзя создавать оборудование не в своём отделении',
            )
    async with async_session() as session:

        query = select(Equipment).where(Equipment.inventory_number == equipment.inventory_number)
        result = await session.execute(query)
        eq = result.scalars().first()
        if eq:
            raise HTTPException(status_code=400, detail='Оборудование с таким инвентарным номером уже существует')

        new_equipment = Equipment(department_id = equipment.department_id,
                            inventory_number=equipment.inventory_number,
                            factory_number=equipment.factory_number,
                            receiving_date=equipment.receiving_date,
                            act_of_receiving=equipment.act_of_receiving,
                            status=equipment.status,
                            type=equipment.type,
                            comment=equipment.comment,
                            )
        session.add(new_equipment)
        await session.flush() 
        await session.refresh(new_equipment, attribute_names=['components']) 
        # if equipment.parent_id:
        #     query = select(Equipment).options(selectinload(Equipment.components)).where(Equipment.id == equipment.parent_id)
        #     result = await session.execute(query)
        #     parent_eq = result.scalars().first()
   
        #     if not parent_eq:
        #         raise HTTPException(status_code=404, detail="Родительский элемент не найден")
        #     parent_eq.components.append(new_equipment)
        #     await session.flush()
        if equipment.childrens:
            for child in equipment.childrens:
                new_child = Equipment(department_id = equipment.department_id,
                            inventory_number=equipment.inventory_number,
                            factory_number=child.get('factory_number'),
                            receiving_date=equipment.receiving_date,
                            act_of_receiving=equipment.act_of_receiving,
                            status=child.get('status'),
                            type=child.get('type'),
                            comment=child.get('comment')
                            )
                session.add(new_child)
                new_equipment.components.append(new_child)
        await session.commit() 
        await session.refresh(new_equipment)  

        return new_equipment

    
async def equipment_update(data, user):
    # if user['department_id'] == 'admin':
    #     raise HTTPException(status_code=400, detail='Админ не может редактировать оборудование')
    # if user['role'] != 'mol':
    #     raise HTTPException(status_code=400, detail='Только МОЛ может редактировать оборудование')
    async with async_session() as session:
        try:
            stmt = select(Equipment).where(Equipment.id == data.updated_equipment.id)
            result = await session.execute(stmt)
            existing_equipment = result.scalars().first()
            if user['department_id'] != str(existing_equipment.department_id):
                if user['department_id'] == 'admin' or user['role'] == 'chief_engineer':
                    pass
                else:
                    raise HTTPException(status_code=400, detail='Вы не можете редактировать не свое оборудование')
            existing_equipment.inventory_number = data.updated_equipment.inventory_number
            existing_equipment.factory_number = data.updated_equipment.factory_number
            existing_equipment.receiving_date = data.updated_equipment.receiving_date
            existing_equipment.act_of_receiving = data.updated_equipment.act_of_receiving
            existing_equipment.status = data.updated_equipment.status
            existing_equipment.type = data.updated_equipment.type
            existing_equipment.comment = data.updated_equipment.comment
            existing_equipment.department_id = data.updated_equipment.department_id

            for child_id in data.deleted_equipments:
                if isinstance(child_id, int):
                    continue
                child_to_delete = await session.get(Equipment, child_id)
                if child_to_delete:
                    await session.delete(child_to_delete)

            for child_data in data.updated_equipment.childrens:
                    # Проверяем, существует ли дочерний элемент        
                    if child_data.get('id') in data.deleted_equipments:
                        continue
                    if not isinstance(child_data.get('id'), int):
                        existing_child = await session.get(Equipment, child_data.get('id'))
                        if existing_child:
                            # Обновляем существующий дочерний элемент
                            existing_child.inventory_number = existing_equipment.inventory_number
                            existing_child.factory_number = child_data.get('factory_number')
                            existing_child.receiving_date = existing_equipment.receiving_date
                            existing_child.act_of_receiving = existing_equipment.act_of_receiving
                            existing_child.status = child_data.get('status')
                            existing_child.type = child_data.get('type')
                            existing_child.comment = child_data.get('comment')
                            existing_child.department_id = existing_equipment.department_id
                    else:
                        # Создаем новый дочерний элемент
                        new_child = Equipment(
                            department_id = existing_equipment.department_id,
                            inventory_number=existing_equipment.inventory_number,
                            factory_number=child_data.get('factory_number'),
                            receiving_date=existing_equipment.receiving_date,
                            act_of_receiving=existing_equipment.act_of_receiving,
                            status=child_data.get('status'),
                            type=child_data.get('type'),
                            comment=child_data.get('comment')
                            )
                        session.add(new_child)
                        await session.refresh(existing_equipment, attribute_names=['components']) 
                        existing_equipment.components.append(new_child)

                # 4. Сохраняем изменения (коммит транзакции)
            await session.commit()
            await session.refresh(existing_equipment)
            return existing_equipment
        except Exception as e:
            print(e)
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при выполнении транзакции в БД: {e}")
        
async def equipment_delete(id, user):
    async with async_session() as session:
        try:
            # 1. Получаем Equipment, которое нужно удалить.  Используем eager loading
            #    чтобы загрузить все связанные components.
            equipment = await session.execute(
                select(Equipment).options(joinedload(Equipment.components)).where(Equipment.id == id)
            )
            equipment = equipment.scalars().first()

            if not equipment:
                raise HTTPException(status_code=404, detail="Equipment not found")

            # 2. Проверка прав доступа (если необходимо)
            if user['role'] == 'mol':
                if user['department_id'] != str(equipment.department_id):
                    raise HTTPException(status_code=400, detail='Вы не можете удалить не свое оборудование')

            # 3. Удаляем связи в таблице equipment_components, связанные с дочерними элементами
            for component in equipment.components:
                stmt_components_delete = delete(equipment_components).where(
                    (equipment_components.c.parent_id == component.id) | (equipment_components.c.component_id == component.id)
                )
                await session.execute(stmt_components_delete)

            # 4. Удаляем дочерние элементы (components) из таблицы Equipment
            for component in equipment.components:
                await session.delete(component)

            # 5. Удаляем связи в таблице equipment_components, связанные с родительским элементом
            stmt_parent_delete = delete(equipment_components).where(
                (equipment_components.c.parent_id == id) | (equipment_components.c.component_id == id)
            )
            await session.execute(stmt_parent_delete)

            # 6. Удаляем Equipment (родительский элемент)
            await session.delete(equipment)
            await session.commit()

        except Exception as e:
            print(e)
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при выполнении транзакции в БД: {e}")


async def get_requests():
    async with async_session() as session:
        stmt = select(EquipmentRequests).order_by(EquipmentRequests.created_at).options(
            selectinload(EquipmentRequests.equipment).options(  # Загружаем Equipment
                selectinload(Equipment.eq_type),  # Загружаем EqType для каждого Equipment
                selectinload(Equipment.department),
                selectinload(Equipment.components).subqueryload(Equipment.department),
                # Загружаем department для компонентов
                selectinload(Equipment.components).subqueryload(Equipment.eq_type),  # Загружаем eq_type для компонентов
            ),selectinload(EquipmentRequests.approval) 
        )
        results = await session.execute(stmt)
        requests = results.scalars().all()
        return requests

async def create_request(equipment_id, type, act, to_department, from_department, user):
    if user['department_id'] == 'admin':
        raise HTTPException(status_code=400, detail='Админ не может создавать запросы')
    if user['role'] != 'mol':
        raise HTTPException(status_code=400, detail='Только МОЛ может создавать запросы')
    if (type == 'transfer') or (type == 'decommissioning'):
        async with async_session() as session:

            stmt = select(Equipment).where(Equipment.id == equipment_id)
            result = await session.execute(stmt)
            existing_equipment = result.scalars().first()
            if user['department_id'] != str(existing_equipment.department_id):
                                raise HTTPException(status_code=400, detail='Вы не можете создать заявку на не свое оборудование')

            stmt = select(EquipmentRequests).where(and_(EquipmentRequests.equipment_id == equipment_id, EquipmentRequests.approval_status == 'pending'))
            result = await session.execute(stmt)
            existing_request = result.scalars().first()
            if existing_request:
                raise HTTPException(status_code=500, detail='Заявка по этому оборудованию уже существует')
            request = EquipmentRequests(request_type=type,
                                        to_department=to_department,
                                        from_department=from_department,
                                        act_of_decommissioning=act,
                                        equipment_id=equipment_id,
                                        user_id=user['id'],
                                        )
            session.add(request)
            await session.commit()
            return {"message": "Заявка успешно создана"}
    else:
        raise HTTPException(status_code=404, detail="Неизвестный тип заявки")
    


async def request_status(id, status, user):
    if user['role'] == 'mol':
        raise HTTPException(status_code=400, detail='МОЛ не может обрабатывать запросы')
    async with async_session() as session:
        stmt = select(EquipmentRequests).where(and_(EquipmentRequests.id == id, EquipmentRequests.approval_status == 'pending'))
        result = await session.execute(stmt)
        request = result.scalars().first()
        if not request:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        try:
            request.approval_status = status
            request.approver_id = user.get('id')
            if status == 'approved':
                stmt = select(Equipment).where(Equipment.id == request.equipment_id).options(selectinload(Equipment.components))
                result = await session.execute(stmt)
                equipment = result.scalars().first()
                
                if request.request_type == 'transfer':
                    stmt = select(Department).where(Department.name == request.to_department)
                    result = await session.execute(stmt)
                    department = result.scalars().first()
                    if department:
                        equipment.department_id = department.id
                        for _child in equipment.components:
                            child = await session.get(Equipment, _child.id)
                            child.department_id = department.id
                    else:
                        equipment.status = "transfered"
                        equipment.act_of_decommissioning = request.act_of_decommissioning
                        equipment.transfer_department = request.to_department
                        for _child in equipment.components:
                            child = await session.get(Equipment, _child.id)
                            child.status = "transfered"
                            child.act_of_decommissioning = request.act_of_decommissioning
                            child.transfer_department = request.to_department
                elif request.request_type == 'decommissioning':
                    equipment.status = "archive"
                    equipment.act_of_decommissioning = request.act_of_decommissioning
                    for _child in equipment.components:
                        child = await session.get(Equipment, _child.id)
                        child.status = "archive"
                        child.act_of_decommissioning = request.act_of_decommissioning
                else:
                    raise HTTPException(status_code=400, detail="Неизвестный тип запроса")
            await session.commit()
            return {"message": "Статус заявки изменен"}
        except Exception as e:
            print(e)
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при выполнении транзакции в БД: {e}")
        

async def delete_request(id, user):
    async with async_session() as session:
        request = await session.get(EquipmentRequests, id)  # Use session.get to fetch the object
        if request:
            if str(request.user_id) == user.get('id'):
                await session.delete(request)  # Use session.delete to delete
                await session.commit()  # Use await session.commit() for async commit
            else:
                raise HTTPException(status_code=403, detail="Недостаточно прав")
        else:
            raise HTTPException(status_code=404, detail="Запрос не найден")
        


async def backup_data(filename="backup.json"):
    async with async_session() as session:
        try:
            stmt = select(Equipment).options(
            selectinload(Equipment.components)
        )
            result = await session.execute(stmt)
            equipments = result.scalars().all()

            # Преобразуем в список словарей
            equipment_data = []
            for item in equipments:
                equipment_data.append({
                    "id": str(item.id),  # Конвертируем UUID в строку
                    "department_id": str(item.department_id) if item.department_id else None,  # Конвертируем UUID в строку
                    "inventory_number": item.inventory_number,
                    "factory_number": item.factory_number,
                    "receiving_date": item.receiving_date.isoformat() if item.receiving_date else None,
                    "act_of_receiving": item.act_of_receiving,
                    "act_of_decommissioning": item.act_of_decommissioning,
                    "status": item.status if item.status else None,  # Получаем значение Enum
                    "transfer_department": item.transfer_department,
                    "type": str(item.type) if item.type else None, #Конвертируем ForeignKey в строку
                    "comment": item.comment,
                    "created_at": item.created_at.isoformat() if item.created_at else None,

                    # Сохраняем только id компонентов (для связи "многие ко многим")
                    "component_ids": [str(component.id) for component in item.components],
                })

            # Сохраняем в JSON файл
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(equipment_data, f, ensure_ascii=False, indent=4)
            

            print(f"Данные успешно сохранены в {filename}")
            return equipment_data

        except Exception as e:
            print(f"Ошибка при создании резервной копии: {e}")



async def restore_data(filename="backup.json"):
    async with async_session() as session:
        try:
            # Читаем данные из JSON файла
            with open(filename, "r", encoding="utf-8") as f:
                equipment_data = json.load(f)

            # Восстанавливаем данные в базе данных
            for item_data in equipment_data:
                # Преобразуем строковые UUID в объекты UUID
                equipment_id = uuid.UUID(item_data.get("id"))
                department_id = uuid.UUID(item_data.get("department_id")) if item_data.get("department_id") else None
                receiving_date = datetime.fromisoformat(item_data.get("receiving_date")) if item_data.get("receiving_date") else None
                created_at = datetime.fromisoformat(item_data.get("created_at")) if item_data.get("created_at") else None
                
                # Создаем объект Equipment
                equipment = Equipment(
                    id=equipment_id,
                    department_id=department_id,
                    inventory_number=item_data.get("inventory_number"),
                    factory_number=item_data.get("factory_number"),
                    receiving_date=receiving_date,
                    act_of_receiving=item_data.get("act_of_receiving"),
                    act_of_decommissioning=item_data.get("act_of_decommissioning"),
                    status=item_data.get("status"),
                    transfer_department=item_data.get("transfer_department"),
                    type=item_data.get("type"),  # Convert ForeignKey to String
                    comment=item_data.get("comment"),
                    created_at=created_at,
                )
                # Получаем список UUID компонентов и добавляем их к equipment (связь many-to-many)
                component_ids = item_data.get("component_ids")
                if component_ids:
                    for component_id in component_ids:
                        component = session.query(Equipment).filter(Equipment.id == uuid.UUID(component_id)).first()
                        if component:
                            equipment.components.append(component)
                session.add(equipment)

            await session.commit()  # Коммитим транзакцию
            print("Данные успешно восстановлены из резервной копии")

        except Exception as e:
            await session.rollback()  # Откатываем транзакцию в случае ошибки
            print(f"Ошибка при восстановлении данных: {e}")
