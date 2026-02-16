from sqlalchemy import Column, String, DateTime, Integer, text, Enum, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import LtreeType
import uuid
from sqlalchemy.types import UserDefinedType
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


Base = declarative_base()
metadata = Base.metadata

class LTree(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "LTREE"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return str(value)
        return process
    
    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            return str(value)
        return process

class EquipmentType(Base):
    __tablename__ = 'equipment_type'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String)
    type = Column(Enum('ssius', 'sius', name='type'), nullable=True)
    classificator_path = Column(LTree(), ForeignKey('classificator.path'))
    
    classificator = relationship("Classificator", back_populates="equipments_type")
    equipment = relationship("Equipment", back_populates='eq_type', cascade="all, delete-orphan")
    fnn = Column(String)
    staff_number = Column(String, nullable=True)

class Classificator(Base):
    __tablename__ = 'classificator'
    path = Column(LTree(), primary_key=True, nullable=False)
    name = Column(String)


    equipments_type = relationship("EquipmentType", back_populates="classificator", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = 'department'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String)
    
    users = relationship("Users", back_populates="department")
    equipments = relationship("Equipment", back_populates="department", cascade="all, delete-orphan") 

class Users(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    department_id = Column(ForeignKey('department.id'))
    role = Column(Enum('head', 'chief_engineer', 'mol', name="users_role_enum"), nullable=False)
    is_superuser = Column(Boolean, default=False)
    password = Column(String, nullable=False)
    department= relationship("Department", back_populates="users")
    # equipments = relationship("Equipment", back_populates='users')


# Association Table (Many-to-Many relationship)
equipment_components = Table(
    'equipment_components', Base.metadata,
    Column('parent_id', UUID(as_uuid=True), ForeignKey('equipment.id'), primary_key=True),
    Column('component_id', UUID(as_uuid=True), ForeignKey('equipment.id'), primary_key=True)
)
    

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    department_id = Column(ForeignKey('department.id'))
    # user_id = Column(ForeignKey('users.id')) 
    inventory_number = Column(String)
    factory_number = Column(String)
    receiving_date = Column(DateTime)
    act_of_receiving = Column(String)
    act_of_decommissioning = Column(String)
    status = Column(Enum('at_work', 'repair', 'archive', 'transfered', name="equipment_status_enum"))
    transfer_department = Column(String, nullable=True)
    type = Column(ForeignKey('equipment_type.id'))
    comment = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    
    department = relationship("Department", back_populates="equipments")
    # users = relationship("Users", back_populates="equipments")
    
        # Many-to-Many relationship with itself (Equipment can have many components and can be a component of many equipments)
    components = relationship(
        "Equipment",
        secondary=equipment_components,
        primaryjoin=id == equipment_components.c.parent_id,
        secondaryjoin=id == equipment_components.c.component_id,
        backref="parents"
    )
    requests = relationship("EquipmentRequests", back_populates="equipment", cascade="all, delete-orphan")

    eq_type = relationship("EquipmentType", back_populates='equipment')
    skzi = relationship("Skzi", back_populates="equipment", cascade="all, delete-orphan")

class Skzi(Base):
    __tablename__ = 'skzi'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"), onupdate=func.now())
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False, unique=True)
    registration_number = Column(String, nullable=False, unique=True)
    act_of_receiving_skzi = Column(String, nullable=True)
    date_of_act_of_receiving = Column(DateTime, nullable=True)
    sertificate_number = Column(String, nullable=True)
    end_date_of_sertificate = Column(DateTime, nullable=True)
    date_of_creation_skzi = Column(DateTime, nullable=True)
    nubmer_of_jornal = Column(String, nullable=True)
    issued_to_whoom = Column(String, nullable=True)

    
    equipment = relationship("Equipment", back_populates="skzi")


class EquipmentRequests(Base):
    __tablename__ = 'equipment_requests'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    request_type = Column(Enum('decommissioning', 'transfer', name="request_type_enum"))
    to_department = Column(String, nullable=True)
    from_department = Column(String, nullable=True)
    act_of_decommissioning = Column(String, nullable=True)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id'))
    user_id = Column(ForeignKey('users.id'))
    approval_status = Column(Enum('pending', 'approved', 'rejected', name="approval_status_enum"), default='pending')
    request_date = Column(DateTime, nullable=False, server_default=text("now()"))
    approver_id = Column(ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    equipment = relationship("Equipment", back_populates="requests")
    # transfer_department_rel = relationship("Department", foreign_keys=[transfer_department],
    #                                        backref="equipment_requests")  # foreign_keys нужно указать явно
    approval = relationship("Users", foreign_keys=[approver_id], backref="approved_requests")  # Вот ОНО!!!
class RefreshTokens(Base):
    __tablename__ = 'refresh_tokens'
    user_id = Column(ForeignKey('users.id'), primary_key=True)
    refresh_token = Column(String, nullable=False)
    users = relationship("Users", uselist=False)




# Таблица для тегов
class Tag(Base):
    __tablename__ = 'tags'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

# Связующая таблица для связи многие-ко-многим между заметками и тегами
note_tags = Table(
    'note_tags', Base.metadata,
    Column('note_id', UUID(as_uuid=True), ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)
)

# Таблица заметок (без связи с оборудованием)
class Note(Base):
    __tablename__ = 'notes'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String)
    author_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"), onupdate=func.now())
    
    # Связи (только автор и теги)
    author = relationship("Users", backref="notes")
    tags = relationship("Tag", secondary=note_tags, backref="notes")