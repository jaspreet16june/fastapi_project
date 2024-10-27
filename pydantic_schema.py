from pydantic import BaseModel
from models import UserRole


class UserSchema(BaseModel):
    email: str
    password: str
    role: UserRole
    
class LoginUserSchema(BaseModel):
    email: str
    password: str
    
    
class FileUpload(BaseModel):
    filename: str

class FileResponse(BaseModel):
    id: int
    filename: str
    encrypted_url: str