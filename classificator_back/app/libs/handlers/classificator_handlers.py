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
                "equipments": [{"id": item.id, "name": item.name, 'type': item.type, 'fnn': item.fnn} for item in classificator.equipments_type]
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
        element.name = name
        await session.commit()
        
        
        
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