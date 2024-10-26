from typing import Optional
from pydantic import BaseModel
from models import UserRole


class UserSchema(BaseModel):
    email: str
    password: str
    role: UserRole