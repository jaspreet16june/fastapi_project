FILE SHARING SYSTEM BETWEEN OPS USER AND CLIENT USER

Framework: FastAPI
Language: Python 
Database: Postgresql

This project aims to provide a robust and secure environment for file sharing between two distinct user roles while ensuring ease of use and strict adherence to security protocols.

-> Set up of project:
1. Create virtual enviornment , Activate the env and install the requirements
2. Hit command pip intsall -r requirement.txt for installing all the required dependencies 
3. Set Up Alembic for Database Migrations: Configure Alembic to manage and apply database migrations.
4. Set Up the PostgreSQL Database:
    Install PostgreSQL if it's not already installed.
    Verify the installation by running:
    "sudo -u postgres psql" to check that psql is installed correctly 
    After that create user in postgres and set up the password for the same.
    Grant all privilges to the created user.

5.  For running the server : command: uvicorn main:app --reload


├── main.py                  # FastAPI app entry point
├── models.py                # SQLAlchemy models
├── pydantic_schema.py               # Pydantic models for request/response
├── database.py              # Database connection and setup
├── auth_utils.py                  # Authentication & JWT handling
├── api ──|
|         |── file_system.py  # File upload/download logic
|         |── login.py         # User login logic
|         |── signup.py         # User signup logic
└── utils.py                 # Utility functions (encryption, validation)

