import bcrypt

from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from pydantic_schema import LoginUserSchema
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal



app = APIRouter()


def get_db():
    """
    Session Management:
    The function creates a new SQLAlchemy session (db = SessionLocal()) when it is called.
    This session is used to interact with the database. After the interaction is complete
    (usually within the scope of an API request), the session is closed (db.close()),
    ensuring that resources are properly released.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/login')
def login_user(user: LoginUserSchema, db: Session = Depends(get_db)):
    """
    Authenticate a user.

    This endpoint allows a verified user to log in by providing their email and password.
    It checks if the user exists, verifies their password, and allows access if successful.

    Parameters:
        user (LoginUserSchema): User login data including email and password.
        db (Session): Database session dependency.

    Returns:
        HTTPException: 200 status code with a success message if login is successful.
        str: Error message if email is not provided.
        HTTPException: 400 status code if the email does not exist or password is incorrect.
    """
    if not user.email:
        return f"User email is mandatory field. Please provide that."
    
    user_exists = db.query(User).filter(User.email == user.email, User.is_verified == True).first()
    
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email id doesn't exists! Please enter correct email.")
        
    encoded_passcode = user.password.encode('utf-8')
    user.password.encode('utf-8')
    if user_exists and bcrypt.checkpw(encoded_passcode, user_exists.hashed_password.encode('utf-8')):
        return HTTPException(status_code=status.HTTP_200_OK, detail="User is successfully logged in!")
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect. Kindly enter the correct password.")
    
