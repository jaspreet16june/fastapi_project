from database import Base
from enum import Enum
from sqlalchemy import String, Integer, Boolean, Column, ForeignKey, Enum as SQLalchemyEnum
from sqlalchemy.orm import relationship

class UserRole(str, Enum):
    OPS_USER = "ops_user"
    CLIENT_USER = "client_user"
    
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLalchemyEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    
    
class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    encrypted_url = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User')
     
    