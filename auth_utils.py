import os
import bcrypt
from datetime import datetime, timedelta
import jwt

# Generate a secure random SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY", "b06175dc14e188825ace71e5abfa0747c9acd02dd3a41cfca5e1991145877f4f")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    This function generates a salt and hashes the provided password using bcrypt.
    Parameters:
        password (str): The plaintext password to be hashed.
    Returns:
        str: The hashed password as a UTF-8 encoded string.
    """
    
    # Generate a salt
    salt = bcrypt.gensalt()
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed_password.decode('utf-8')

def create_verification_token(email: str):
    """
    Create a JWT verification token for email verification.
    Generates a JWT token containing the user's email as the subject and an expiration time.
    Parameters:
        email (str): The user's email address to encode in the token.
    Returns:
        str: A JWT token as a string.
    """
    # By default the token expiration time is 1 hour but this is dynamically configured so it can be increase.
    expire = datetime.now() + timedelta(hours=os.getenv("TOKEN_EXPIRATION_TIME", 1)) 
    encoding = {"sub": email, "exp": expire}
    return jwt.encode(encoding, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    """
    Decode a JWT token.
    Decodes a JWT token to retrieve its contents, such as the email subject.
    Parameters:
        token (str): The JWT token to decode.
    Returns:
        dict: The decoded JWT data containing the user's email and expiration details.
    """
    reset_token_data = jwt.decode(token, algorithms=ALGORITHM, key=SECRET_KEY)
    return reset_token_data