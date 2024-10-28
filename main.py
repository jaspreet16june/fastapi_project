import bcrypt
from fastapi.responses import FileResponse
from database import SessionLocal
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
import os

from pydantic_schema import LoginUserSchema, UserSchema
from auth_utils import create_verification_token, decode_jwt, hash_password
from sqlalchemy.orm import Session
from models import Files, User, UserRole

from utils import send_verification_email
from utils import generate_encrypted_url  



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
    


@app.post("/upload-file")
async def upload_file(email:str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a file for the current user.

    This endpoint allows an Ops User to upload files with specific file types (docx, xlsx, pptx).
    It validates the user’s role and file type, saves the file, and stores an encrypted URL in the database.

    Parameters:
        email (str): Email of the user uploading the file.
        file (UploadFile): File to be uploaded.
        db (Session): Database session dependency.

    Returns:
        dict: Success message and the encrypted URL of the uploaded file.
        HTTPException: 403 status code if the user is not authorized.
        HTTPException: 400 status code if the file type is invalid.
    """
    
    # Check if the current user is an client user
    current_user = db.query(User).filter(User.email == email).first()
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="You are not authorized to upload files.")

    # Validate file type
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",       # xlsx
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"  # pptx
    ]:
        raise HTTPException(status_code=400, detail="Only pptx, docx, and xlsx files are allowed.")

    UPLOAD_DIRECTORY = "/tmp/path/to/your/files/"
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    
    file_location = f"{UPLOAD_DIRECTORY}{file.filename}"
    
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    # Generate an encrypted URL for the uploaded file
    encrypted_url = generate_encrypted_url(file.filename)

    # Save the encrypted URL in the database
    # Assuming you have a File model to save the details
    new_file_entry = Files(
        file_name=file.filename,
        encrypted_url=encrypted_url,
        user_id=current_user.id  
    )
    db.add(new_file_entry)
    db.commit()
    db.refresh(new_file_entry)

    return {"detail": "File uploaded successfully!", "encrypted_url": encrypted_url}

@app.get("/download-file/{file_id}")
async def download_file(email: str, file_id: int, db: Session = Depends(get_db)):
    """
    Download a file for a client user.

    This endpoint allows a Client User to download a file by providing their email and the file ID.
    It checks if the file exists and verifies the user's role before providing an encrypted URL.

    Parameters:
        email (str): Email of the user downloading the file.
        file_id (int): ID of the file to be downloaded.
        db (Session): Database session dependency.

    Returns:
        dict: Encrypted URL of the requested file.
        HTTPException: 404 status code if the file is not found.
        HTTPException: 403 status code if the user is not authorized.
    """
    file_entry = db.query(Files).filter(Files.id == file_id).first()

    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found.")
    
    if file_entry.user.role == UserRole.OPS_USER:
        raise HTTPException(status_code=403, detail="You are not authorized to download files.")

    file_path = os.path.join("/tmp/path/to/your/files/", file_entry.file_name)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(file_path, media_type='application/octet-stream', filename=file_entry.file_name)


@app.get("/list-files")
async def list_files(email: str, db: Session = Depends(get_db)):
    """
    List all uploaded files for a client user.

    This endpoint allows a Client User to view a list of all uploaded files.
    It checks the user's role before returning the list of files.

    Parameters:
        email (str): Email of the user requesting the file list.
        db (Session): Database session dependency.

    Returns:
        list: List of file records from the database.
        HTTPException: 403 status code if the user is not authorized.
    """
    current_user = db.query(User).filter(User.email == email).first()
    if current_user.role == UserRole.OPS_USER:
        raise HTTPException(status_code=403, detail="You are not authorized to view files.")

    # Query the database for all files
    files = db.query(Files).all()
    
    return files 
