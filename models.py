from database import Base
from sqlalchemy import String, Integer, Boolean, Column

class User(Base):
    __tablename__ = "USER"
    id=Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)