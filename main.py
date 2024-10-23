from fastapi import FastAPI
from pydantic_schema import User

app = FastAPI()

@app.get('/', status_code=200)
def get_user(id:int=None):
    return f"user exists with this id: {id}"


@app.post("/create_user", status_code=201)
def create_user(user:User):
    return {
        "id":user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "mobile_no": user.mobile_number
    }