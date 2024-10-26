import bcrypt
import jwt
from datetime import datetime, timedelta

secret_key = "" 
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    # Generate a salt
    salt = bcrypt.gensalt()
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed_password.decode('utf-8')

def create_verification_token(email: str):
    expire = datetime.now() + timedelta(hours=1) #This token is valid for only 1 hour 
    encoding = {"sub": email, "exp": expire}
    return jwt.encode(encoding, secret_key, algorithm=ALGORITHM)

# create secert key 