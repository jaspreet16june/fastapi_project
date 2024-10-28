from api import login, signup, file_system
from database import SessionLocal
from fastapi import APIRouter, FastAPI

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

app = FastAPI(title="File Sharing System")
api_router = APIRouter()

# Include the routers from login, signup, and file_system into the api_router
api_router.include_router(signup.app, tags=['SIGNUP'], prefix="/api/v1")
api_router.include_router(login.app, tags=['LOGIN'], prefix="/api/v1")
api_router.include_router(file_system.app, tags=['FILE SYSTEM'], prefix="/file_system")

# Include the api_router into the main app
app.include_router(api_router)
