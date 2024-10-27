from fastapi import FastAPI, Depends, HTTPException, status

from pydantic_schema import UserSchema
from password import create_verification_token, decode_jwt, hash_password
from database import SessionLocal
from sqlalchemy.orm import Session
from models import User
from utils import send_verification_email




app = FastAPI()


# Usage of this:: Session Management:
# The function creates a new SQLAlchemy session (db = SessionLocal()) when it is called. This session is used to interact with the database.
# After the interaction is complete (usually within the scope of an API request), the session is closed (db.close()), ensuring that resources are properly released.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        

@app.post('/signup', status_code=201)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    user_data = user
    if not user_data.email:
        return f"User email is mandatory field. Please provide me that."
    
    user_exists = db.query(User).filter(User.email == user.email).first()
    
    if user_exists:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email id already exists! Please enter other email.")
        
    password = hash_password(user_data.password)
    
    new_user_instance = User(email=user_data.email, hashed_password=password, role=user_data.role)
    db.add(new_user_instance)
    db.commit()
    db.refresh(new_user_instance) #If your User model has an auto-incrementing primary key (id), it won’t be set on new_user until you refresh it.
    
    ## Now sent the verification mail to user:
    #step 1: create a verification token using jwt 
    token = create_verification_token(user_data.email)
    verification_url = f"http://localhost:8080/verify?token={token}"
    send_verification_email(user_data.email, verification_url)
    
    return HTTPException(status_code=status.HTTP_201_CREATED, detail="User is successfully signed in!")




@app.get('/verify', status_code=200)
async def verify(token: str, db: Session = Depends(get_db)):
    verify_token_dict = decode_jwt(token)
    
    user_exist = db.query(User).filter(User.email ==verify_token_dict['sub']).first()
    
    if not user_exist:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email id doesn't exists! Please enter the correct email.")
    
    user_exist.is_verified = True
    db.commit()
    return "Token Verify successfully!"
    
    