import os
import secrets
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload, joinedload
from app.libs.postgres.models import *
from app.schemas.schema import NoteCreateSchema, NoteUpdateSchema, NoteSearchSchema, TagCreate, TagResponse, TagUpdateSchema
from fastapi import HTTPException
from sqlalchemy import and_, or_
from app.settings import get_settings



settings = get_settings()
async_session = settings.async_session


async def get_notes(search: NoteSearchSchema):
    async with async_session() as session:
        stmt = select(Note).options(
            joinedload(Note.author),
            selectinload(Note.tags)
        ).order_by(Note.created_at.desc())
        
        # Применяем фильтры поиска
        conditions = []
        
        if search.query:
            search_pattern = f"%{search.query}%"
            conditions.extend([
                Note.title.ilike(search_pattern),
                Note.content.ilike(search_pattern)
            ])
        
        if search.tags:
            # Ищем заметки, у которых есть хотя бы один из указанных тегов
            for tag_name in search.tags:
                tag_condition = Note.tags.any(Tag.name == tag_name)
                conditions.append(tag_condition)
        
        if conditions:
            stmt = stmt.where(or_(*conditions))
        
        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Применяем пагинацию
        stmt = stmt.limit(search.limit).offset(search.offset)
        
        result = await session.execute(stmt)
        notes = result.unique().scalars().all()
        
        return {'notes': notes, 'total_count': total_count}

async def create_note(note: NoteCreateSchema, user):
    async with async_session() as session:
        try:
            # Создаем новую заметку
            new_note = Note(
                title=note.title,
                content=note.content,
                author_id=user['id']
            )
            
            # Обрабатываем теги
            if note.tags:
                for tag_name in note.tags:
                    # Ищем существующий тег или создаем новый
                    tag_stmt = select(Tag).where(Tag.name == tag_name)
                    tag_result = await session.execute(tag_stmt)
                    existing_tag = tag_result.scalars().first()
                    
                    if not existing_tag:
                        existing_tag = Tag(name=tag_name)
                        session.add(existing_tag)
                        await session.flush()
                    
                    new_note.tags.append(existing_tag)
            
            session.add(new_note)
            await session.commit()
            await session.refresh(new_note, attribute_names=['tags', 'author'])
            
            return new_note
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при создании заметки: {e}")

async def update_note(note_id: str, note_data: NoteUpdateSchema, user):
    async with async_session() as session:
        try:
            # Получаем существующую заметку
            stmt = select(Note).options(selectinload(Note.tags)).where(Note.id == note_id)
            result = await session.execute(stmt)
            existing_note = result.scalars().first()
            
            if not existing_note:
                raise HTTPException(status_code=404, detail="Заметка не найдена")
            
            # Проверяем права доступа
            if str(existing_note.author_id) != user['id'] and user['department_id'] != 'admin':
                raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования этой заметки")
            
            # Обновляем поля
            if note_data.title is not None:
                existing_note.title = note_data.title
            if note_data.content is not None:
                existing_note.content = note_data.content
            
            # Обновляем теги если они переданы
            if note_data.tags is not None:
                # Очищаем текущие теги
                existing_note.tags.clear()
                
                # Добавляем новые теги
                for tag_name in note_data.tags:
                    tag_stmt = select(Tag).where(Tag.name == tag_name)
                    tag_result = await session.execute(tag_stmt)
                    existing_tag = tag_result.scalars().first()
                    
                    if not existing_tag:
                        existing_tag = Tag(name=tag_name)
                        session.add(existing_tag)
                        await session.flush()
                    
                    existing_note.tags.append(existing_tag)
            
            existing_note.updated_at = datetime.now()
            
            await session.commit()
            await session.refresh(existing_note, attribute_names=['tags', 'author'])
            
            return existing_note
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении заметки: {e}")

async def delete_note(note_id: str, user):
    async with async_session() as session:
        try:
            note = await session.get(Note, note_id)
            
            if not note:
                raise HTTPException(status_code=404, detail="Заметка не найдена")
            
            # Проверяем права доступа
            if str(note.author_id) != user['id'] and user['department_id'] != 'admin':
                raise HTTPException(status_code=403, detail="Недостаточно прав для удаления этой заметки")
            
            await session.delete(note)
            await session.commit()
            
            return {"message": "Заметка успешно удалена"}
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении заметки: {e}")

async def get_tags():
    async with async_session() as session:
        stmt = select(Tag).order_by(Tag.name)
        result = await session.execute(stmt)
        tags = result.scalars().all()
        return tags
    

async def update_tag(tag_id: str, tag_data: TagCreate, user):
    async with async_session() as session:
        try:
            # Получаем существующий тег
            tag = await session.get(Tag, tag_id)
            
            if not tag:
                raise HTTPException(status_code=404, detail="Тег не найден")
            
            # Проверяем, не существует ли тег с таким же именем
            if tag_data.name != tag.name:
                existing_tag_stmt = select(Tag).where(Tag.name == tag_data.name)
                existing_tag_result = await session.execute(existing_tag_stmt)
                existing_tag = existing_tag_result.scalars().first()
                
                if existing_tag:
                    raise HTTPException(status_code=400, detail="Тег с таким именем уже существует")
            
            # Обновляем тег
            tag.name = tag_data.name
            await session.commit()
            await session.refresh(tag)
            
            return tag
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении тега: {e}")

async def delete_tag(tag_id: str, user):
    async with async_session() as session:
        try:
            # Получаем тег вместе с заметками
            stmt = select(Tag).options(selectinload(Tag.notes)).where(Tag.id == tag_id)
            result = await session.execute(stmt)
            tag = result.scalars().first()
            
            if not tag:
                raise HTTPException(status_code=404, detail="Тег не найден")
            
            # Проверяем, есть ли связанные заметки
            if tag.notes and len(tag.notes) > 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Невозможно удалить тег. С ним связано {len(tag.notes)} заметок."
                )
            
            # Если заметок нет - удаляем тег
            await session.delete(tag)
            await session.commit()
            
            return {"message": "Тег успешно удален"}
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении тега: {e}")