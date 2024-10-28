from fastapi.responses import FileResponse
from fastapi import APIRouter, FastAPI, Depends, HTTPException, UploadFile, File
import os

from sqlalchemy.orm import Session
from models import Files, User, UserRole

from utils import generate_encrypted_url  
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
