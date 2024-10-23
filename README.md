Fast API: Python Framework
How to Setup database.py file (means How to setup database)
1) Install postgres.
2) Then access to postgres SQL
    Sudo -u postgres psql
3) create User new-user username with "Test@123"; password
4) Create database file shaving-bd database name Owner (username>,
5) GRANT all prèvilges on Database CDB-name > to <username>,
6) Make DATABASE_URL:
   postgresql:// <username>: Password (@localhost: 5432 (Database name>
7) Base declartive-base()
8) session Local = Sessionmaker (bind= engine)

Intsall : fastapi, psycopg2-binary, SQLAlchemy, alembic, pydantic
Make virtual enviornment by using virtualenv new_env
Activate the enviornment always while working on this project 

command: uvicorn main:app --reload
