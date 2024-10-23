from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    mobile_number: str