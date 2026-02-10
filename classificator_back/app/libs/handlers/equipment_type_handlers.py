import logging
from pprint import pprint
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, text
from uuid import UUID
from app.settings import get_settings
from app.libs.postgres.models import Classificator, EquipmentType
from sqlalchemy.sql import func
from typing import List, Dict, Optional
from app.libs.handlers.classificator_handlers import check_descendants
from sqlalchemy import exists

settings = get_settings()
async_session = settings.async_session


async def create_equipment_type(name: str, classificator_path: str, type: Optional[str] = None, fnn: str = None):
    async with async_session() as session:
        query = select(exists(Classificator).where(Classificator.path == classificator_path))
        result = await session.execute(query)
        classificator_exists = result.scalar_one_or_none()
  
        if not classificator_exists:
            return False, f"Classificator with path '{classificator_path}' does not exist"
        if not await check_descendants(classificator_path):
            return False, f"У классификатора есть потомки"
        try:
          session.add(EquipmentType(name=name, classificator_path=classificator_path, type=type, fnn=fnn))
          await session.commit()
          return True, None
        except Exception as e:
          await session.rollback()
          return False, f"Failed to create equipment '{name}': {e}"
        


async def get_equipment_type(name: str = None):
    async with async_session() as session:
        if name:
            query = select(EquipmentType).where(func.lower(EquipmentType.name).ilike(f"%{name.lower()}%"))
            results = await session.execute(query)
        else:
             query = select(EquipmentType)
             results = await session.execute(query)
        equipment = results.scalars().all()
        return equipment


async def get_equipment_type_by_path(path: str):
    async with async_session() as session:
        query = select(EquipmentType).where(EquipmentType.classificator_path == path)
        results = await session.execute(query)
        equipment = results.scalars().all()
        return equipment


async def update_equipment_type(equipment_id: UUID, name: str = None, fnn: str = None, type: str = None):
    async with async_session() as session:
        try:
            query = select(EquipmentType).where(EquipmentType.id == equipment_id)
            result = await session.execute(query)
            equipment = result.scalar_one_or_none()
            if not equipment:
                return False, f"Equipment with id '{equipment_id}' does not exists"
            equipment.name = name
            equipment.fnn = fnn
            equipment.type = type if type else None
            await session.commit()
            return True, None
        except Exception as e:
           await session.rollback()
           return False, f"Failed to update equipment with id '{equipment_id}': {e}"
    
    

async def delete_equipment_type(equipment_id: UUID):
    async with async_session() as session:
        try:
            query = select(EquipmentType).where(EquipmentType.id == equipment_id)
            result = await session.execute(query)
            equipment = result.scalar_one_or_none()
            if not equipment:
                return False, f"Equipment with id '{equipment_id}' does not exists"
            await session.delete(equipment)
            await session.commit()
            return True, None
        except Exception as e:
           await session.rollback()
           return False, f"Failed to delete equipment with id '{equipment_id}': {e}"
    