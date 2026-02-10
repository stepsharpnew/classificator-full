from typing import Any, Optional, Annotated, List, ForwardRef
from enum import Enum
from pydantic import BaseModel, field_validator, StringConstraints, UUID4
from datetime import date, datetime

class EquipmentType(str, Enum):
    ssius = "ssius"
    sius = "sius"
    


class Response(BaseModel):
    data: Optional[Any]
    error: Optional[Any]
    success: bool
    


class ClassificatorModel(BaseModel):
    path: Annotated[str, StringConstraints(pattern=r"^\d+(\.\d+)*$")]
    name: str

    @field_validator('path')
    def validate_ltree_format(cls, path):
        parts = path.split('.')
        for part in parts:
            if not part.isdigit():
                raise ValueError("LTREE path parts must be digits")
        return path
    
class UsersResponseSchema(BaseModel):
    id: str
    login: str
    first_name: str
    last_name: str
    department_id: str
    role: str
    is_superuser: bool


class UsersRegisterSchema(BaseModel):
    login: str
    first_name: str
    last_name: str
    department_id: str
    role: str
    password: str
    

class EquipmentStatus(str, Enum):
    at_work = 'at_work'
    repair = 'repair'
    archive = 'archive'


class EquipmentCreateSchema(BaseModel):
    department_id: str
    inventory_number: str
    factory_number: str
    receiving_date: date
    act_of_receiving: str
    status: EquipmentStatus
    type: str
    comment: Optional[str] = None
    parent_id: Optional[str] = None
    childrens: Optional[list[Any]] = None

class EquipmentUpdateSchema(BaseModel):
    id: str
    department_id: str
    inventory_number: str
    factory_number: str
    receiving_date: date
    act_of_receiving: str
    status: EquipmentStatus
    type: str
    comment: Optional[str] = None
    parent_id: Optional[str] = None
    childrens: Optional[list[Any]] = None


class EquipmentUpdateDataSchema(BaseModel):
    updated_equipment: EquipmentUpdateSchema
    deleted_equipments: Optional[list] = None

class DepartmentSchema(BaseModel):
    id: str
    name: str

class EquipmentResponseSchema(BaseModel):
    id: str
    inventory_number: str
    factory_number: str
    receiving_date: date
    user_id: str
    act_of_receiving: str
    status: EquipmentStatus
    type: str
    comment: Optional[str] = None
    components: Optional[Any] = None
    department: Optional[Any] = None
    # components: Optional[List[ForwardRef('EquipmentResponseSchema')]] = None
    # department: DepartmentSchema


class TagCreate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

class NoteCreateSchema(BaseModel):
    title: str
    content: str
    tags: List[str] = []  # список названий тегов

class NoteUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteResponseSchema(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime

class NoteSearchSchema(BaseModel):
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20
    offset: int = 0


class TagCreate(BaseModel):
    name: str

class TagUpdateSchema(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    notes_count: Optional[int] = 0  # Добавляем счетчик заметок