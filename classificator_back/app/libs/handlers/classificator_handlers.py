import logging
from pprint import pprint
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, text
from sqlalchemy import exists
from app.settings import get_settings
from app.libs.postgres.models import Classificator, EquipmentType
from app.schemas.schema import Response, ClassificatorModel
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
settings = get_settings()
async_session = settings.async_session

# async def transform_to_tree(classificators):
#     tree = {}
#     sorted_classificators = sorted(classificators, key=lambda x: x.path)
    
#     for classificator in sorted_classificators:
#         current_level = tree
#         path_parts = classificator.path.split(".")
#         for i, part in enumerate(path_parts):
#             if part not in current_level:
#                 current_level[part] = {}
#             if i == len(path_parts) - 1:
#                 current_level[part]["name"] = classificator.name
#             current_level = current_level[part]
#     return tree


async def get_classification(path: str = None):
   async with async_session() as session:
        if path:
            query = select(Classificator).where(text(f"path <@ '{path}'")).order_by(Classificator.path)
        else:
            query = select(Classificator).order_by(Classificator.path).options(
        selectinload(Classificator.equipments_type))
        results = await session.execute(query)
        classificators = results.scalars().all()

        #Сортировка через питон по пути
        

        classificators.sort(key=ltree_key)

        result = []
        for classificator in classificators:
            result.append({
                "id": classificator.path,
                "name": classificator.name,
                "path": classificator.path,
                "equipments": [{"id": item.id, "name": item.name, 'type': item.type, 'fnn': item.fnn, 'staff_number': item.staff_number} for item in classificator.equipments_type]
            })
        return Response(data=result, success=True, error=None)

#Сортировка через питон по пути
def ltree_key(classificator):
    parts = classificator.path.split('.')
    return [int(part) for part in parts]

async def get_classification_leaf():
   async with async_session() as session:
       
        query = select(Classificator).order_by('path')
        results = await session.execute(query)
        classificators = results.scalars().all()
        classificators.sort(key=ltree_key)
        result = []
        for classificator in classificators:
            if (await check_descendants(classificator.path)):
                result.append({
                    "id": classificator.path,
                    "name": classificator.name,
                    "path": classificator.path 
                })
        return Response(data=result, success=True, error=None)



async def create_classification(path: str, name: str):
    try:
        data = ClassificatorModel(path=path, name=name)
    except ValidationError as exc:
        return Response(data=None, success=False, error={'code': 10003, 'msg' : f"Неверный формат пути '{path}'"})
    async with async_session() as session:
        path_parts = data.path.split(".")
        if len(path_parts) > 1:
            parent_path = ".".join(path_parts[:-1])
            query = select(Classificator).where(Classificator.path == parent_path)
            result = await session.execute(query)
            parent_exists = result.scalar_one_or_none()
            if not parent_exists:
                return Response(data=None, success=False, error={'code': 10001, 'msg' : f"Родительский элемент {parent_path} не существует "})
        try:
            session.add(Classificator(path=data.path, name=data.name))
            await session.commit()
            return Response(data=f"Классификация {path} создана", success=True, error=None)
        except IntegrityError as exc:
            await session.rollback()
            return Response(data=None, success=False, error={'code': 10002, 'msg' : f"Классификация {path} уже существует"})

async def delete_classification(path: str):
    async with async_session() as session:
        # Получение элемента, который нужно удалить
        query = select(Classificator).where(Classificator.path == path)
        result = await session.execute(query)
        parent_element = result.scalar_one_or_none()
        
        if parent_element:
           # Получение всех дочерних элементов
            child_query = select(Classificator).where(text(f"path <@ '{path}' AND path != '{path}'"))
            child_results = await session.execute(child_query)
            child_elements = child_results.scalars().all()

            for child in child_elements:
                await session.delete(child)
            
            await session.delete(parent_element)
            await session.commit()

async def check_descendants(path):
    """Check if a classificator has descendants using fully manual SQL."""
    async with async_session() as session:
        result = await session.execute(text(
            f"""
            SELECT NOT EXISTS (
                SELECT 1
                FROM classificator
                WHERE path <@ '{path}' AND path != '{path}'
            )
            """
        ))
        descendant_not_exists = result.scalar()
        return descendant_not_exists
    

async def update_classification(path: str, name: str):
    async with async_session() as session:
        query = select(Classificator).where(Classificator.path == path)
        result = await session.execute(query)
        element = result.scalar_one_or_none()
        if not element:
            return Response(data=None, success=False, error={'msg': f"Классификация {path} не найдена"})
        element.name = name
        await session.commit()
        return Response(data=f"Классификация {path} обновлена", success=True, error=None)


async def rename_classification_path(old_path: str, new_path: str):
    """Переименование пути классификации с каскадным обновлением всех потомков и EquipmentType."""
    # Валидация формата нового пути
    try:
        ClassificatorModel(path=new_path, name="validation")
    except ValidationError:
        return Response(data=None, success=False, error={'msg': f"Неверный формат пути '{new_path}'"})

    async with async_session() as session:
        # 1. Проверяем, что исходная классификация существует
        result = await session.execute(
            text("SELECT path::text, name FROM classificator WHERE path::text = :old_path OR path::text LIKE :prefix ORDER BY path"),
            {"old_path": old_path, "prefix": f"{old_path}.%"}
        )
        rows = result.fetchall()

        if not rows:
            return Response(data=None, success=False, error={'msg': f"Классификация {old_path} не найдена"})

        # 2. Строим маппинг старый путь → новый путь
        mapping = {}
        for path_str, name in rows:
            new_p = new_path + path_str[len(old_path):]
            mapping[path_str] = (new_p, name)

        # 3. Проверяем, что ни один из новых путей не занят (кроме тех, которые сами переименовываются)
        old_paths_set = set(mapping.keys())
        for new_p, _ in mapping.values():
            if new_p in old_paths_set:
                # Этот путь сам переименовывается — пропускаем
                continue
            check = await session.execute(
                text("SELECT EXISTS(SELECT 1 FROM classificator WHERE path::text = :p)"),
                {"p": new_p}
            )
            if check.scalar():
                return Response(data=None, success=False, error={
                    'msg': f"Классификация {new_p} уже существует, переименование невозможно"
                })

        # 4. Проверяем, что родитель нового пути существует (если есть родитель)
        new_parts = new_path.split('.')
        if len(new_parts) > 1:
            parent_new = '.'.join(new_parts[:-1])
            new_paths_set = set(v[0] for v in mapping.values())
            if parent_new not in new_paths_set:
                check = await session.execute(
                    text("SELECT EXISTS(SELECT 1 FROM classificator WHERE path::text = :p)"),
                    {"p": parent_new}
                )
                if not check.scalar():
                    return Response(data=None, success=False, error={
                        'msg': f"Родительский элемент {parent_new} не существует"
                    })

        # 5. Выполняем переименование:
        #    a) Создаём новые записи classificator
        #    b) Перенаправляем equipment_type на новые пути
        #    c) Удаляем старые записи classificator
        try:
            # a) Вставляем новые classificator (от корня к листьям)
            sorted_paths = sorted(mapping.keys(), key=lambda p: len(p.split('.')))
            for old_p in sorted_paths:
                new_p, name = mapping[old_p]
                await session.execute(
                    text("INSERT INTO classificator (path, name) VALUES (CAST(:path AS ltree), :name)"),
                    {"path": new_p, "name": name}
                )

            # b) Обновляем equipment_type ссылки
            for old_p in sorted_paths:
                new_p, _ = mapping[old_p]
                await session.execute(
                    text("UPDATE equipment_type SET classificator_path = CAST(:new_p AS ltree) WHERE classificator_path::text = :old_p"),
                    {"new_p": new_p, "old_p": old_p}
                )

            # c) Удаляем старые classificator (от листьев к корню)
            for old_p in reversed(sorted_paths):
                await session.execute(
                    text("DELETE FROM classificator WHERE path::text = :old_p"),
                    {"old_p": old_p}
                )

            await session.commit()
            return Response(
                data=f"Нумерация изменена: {old_path} → {new_path}",
                success=True,
                error=None
            )
        except IntegrityError as exc:
            await session.rollback()
            return Response(data=None, success=False, error={
                'msg': f"Ошибка при переименовании: конфликт путей"
            })
        except Exception as exc:
            await session.rollback()
            return Response(data=None, success=False, error={
                'msg': f"Ошибка при переименовании: {str(exc)}"
            })
        
        
        
async def get_classification_tree():
    async with async_session() as session:
        classificators = await session.execute(select(Classificator).order_by('path'))
        classificators = classificators.scalars().all()
        equipment = await _get_equipment_type(session)  # Get all equipment once

        # Create a dictionary to store nodes by their path
        node_map = {c.path: {"id": c.path, "name": c.name, "path": c.path, "equipments": [], "children": []} for c in classificators}

        # Add equipment to the corresponding nodes
        for item in equipment:
            if item.classificator_path in node_map:
                node_map[item.classificator_path]["equipments"].append({'id': item.id, 'name': item.name, 'fnn': item.fnn})

        # Build the tree structure
        tree = []
        for c in classificators:
            node = node_map[c.path]
            parent_path = ".".join(c.path.split(".")[:-1])
            if parent_path in node_map:
                node_map[parent_path]["children"].append(node)
            else:
                tree.append(node)  # Root node

        return Response(data=tree, success=True, error=None)
    
async def _get_equipment_type(session, name: str = None):
    query = select(EquipmentType).order_by(EquipmentType.id)
    if name:
        query = query.where(EquipmentType.name == name)
    result = await session.execute(query)
    return result.scalars().all()