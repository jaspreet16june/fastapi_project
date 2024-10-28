from auth_utils import create_verification_token, decode_jwt, hash_password
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from pydantic_schema import UserSchema
from sqlalchemy.orm import Session
from models import User
from utils import send_verification_email
from database import SessionLocal




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

app = APIRouter()  

@app.post('/signup', status_code=201)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint allows a new user to sign up by providing their email, password, and role.
    It checks if the email is already in use, hashes the password, creates a new user record,
    and sends a verification email with a token.

    Parameters:
        user (UserSchema): User data including email, password, and role.
        db (Session): Database session dependency.

    Returns:
        HTTPException: 201 status code with a success message on successful signup.
        str: Error message if email is not provided.
    """
    
    if not user.email:
        return f"User email is mandatory field. Please provide that."
    
    user_exists = db.query(User).filter(User.email == user.email).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email id already exists! Please enter other email.")
        
    password = hash_password(user.password)
    
    new_user_instance = User(email=user.email, hashed_password=password, role=user.role)
    db.add(new_user_instance)
    db.commit()
    #If your User model has an auto-incrementing primary key (id), it won’t be set on new_user until you refresh it.
    db.refresh(new_user_instance) 
    
    # Now sent the verification mail to user:
    #step 1: create a verification token using jwt 
    token = create_verification_token(user.email)
    # Step 2: Send the verification email to the user
    verification_url = f"http://localhost:8080/verify?token={token}"
    send_verification_email(user.email, verification_url)
    
    return HTTPException(status_code=status.HTTP_201_CREATED, detail="User is successfully signed up! A verification email has been sent.")




@app.get('/verify', status_code=200)
async def verify(token: str, db: Session = Depends(get_db)):
    """
    Verify a user's email using a token.

    This endpoint verifies the user's email address using a token sent via email.
    It decodes the token, checks if the user exists, and updates the user's status to verified.

    Parameters:
        token (str): JWT token containing the user's email.
        db (Session): Database session dependency.

    Returns:
        str: Success message if the token is verified.
        HTTPException: 400 status code if the email does not exist.
    """
    verify_token_dict = decode_jwt(token)
    
    user_exist = db.query(User).filter(User.email ==verify_token_dict['sub']).first()
    
    if not user_exist:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email id doesn't exists! Please enter the correct email.")
    
    user_exist.is_verified = True
    db.commit()
    return "Token Verify successfully!"
    
    