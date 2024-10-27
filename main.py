import bcrypt
import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File

from pydantic_schema import LoginUserSchema, UserSchema
from password import create_verification_token, decode_jwt, hash_password
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Files, User, UserRole
from utils import send_verification_email
from utils import generate_encrypted_url  
from fastapi.responses import FileResponse




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
    
    
    
@app.post('/login')
def login_user(user: LoginUserSchema, db: Session = Depends(get_db)):
    user_data = user
    if not user_data.email:
        return f"User email is mandatory field. Please provide me that."
    
    user_exists = db.query(User).filter(User.email == user.email, User.is_verified == True).first()
    
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email id doesn't exists! Please enter correct email.")
        
    encoded_passcode = user_data.password.encode('utf-8')
    user_data.password.encode('utf-8')
    if user_exists and bcrypt.checkpw(encoded_passcode, user_exists.hashed_password.encode('utf-8')):
        return HTTPException(status_code=status.HTTP_200_OK, detail="User is successfully logged in!")
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect. Kindly enter the correct password.")
    


@app.post("/upload-file")
async def upload_file(email:str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    # Check if the current user is an Ops User
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
    
    file_entry = db.query(Files).filter(Files.id == file_id).first()

    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found.")
    
    current_user = db.query(User).filter(User.email == email).first()
    if current_user.role == UserRole.OPS_USER:
        raise HTTPException(status_code=403, detail="You are not authorized to download files.")


    file_path = os.path.join("/tmp/path/to/your/files/", file_entry.file_name)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return {"encrypted_url": file_entry.encrypted_url}  # Return the encrypted URL for the file
    # return FileResponse(file_path, media_type='application/octet-stream', filename=file_entry.file_name)


@app.get("/list-files")
async def list_files(email: str, db: Session = Depends(get_db)):
    
    current_user = db.query(User).filter(User.email == email).first()
    if current_user.role == UserRole.OPS_USER:
        raise HTTPException(status_code=403, detail="You are not authorized to view files.")

    # Query the database for all files
    files = db.query(Files).all()
    
    return files 
