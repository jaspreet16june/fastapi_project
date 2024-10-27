import bcrypt
from datetime import datetime, timedelta
import jwt

# Generate a secure random SECRET_KEY
SECRET_KEY = 'b06175dc14e188825ace71e5abfa0747c9acd02dd3a41cfca5e1991145877f4f'
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
    return jwt.encode(encoding, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    reset_token_data = jwt.decode(token, algorithms=ALGORITHM, key=SECRET_KEY)

    return reset_token_data