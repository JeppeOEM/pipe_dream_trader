
# JWT Structure
# Possible to extend both headers and payload
# Header{
#  "alg": "HS256",
#  "typ": "JWT"
#}
# {
#{
#  "sub": "1234567890",
#  "name": "John Doe",
#  "role": "Admin"    # make up what ever roles you want
#  "iat": 1516239022
#}
# And a Signature that verifies the token authenticity
#HMACSHA256(
#  base64UrlEncode(header) + "." + base64UrlEncode(payload),
#  "mysecret"
#)
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from ...models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ...config import Config 



class AuthService:
    class CreateUserRequest(BaseModel):
        username: str
        email: str
        first_name: str
        last_name: str
        password: str
        role: str
        phone_number: str

    class Token(BaseModel):
        access_token: str
        token_type: str
    oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
    def __init__(self):
        # Initialize bcrypt and OAuth2 password bearer
        self.bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def authenticate_user(self, username: str, password: str, db):
        # Authenticate user credentials
        user = db.query(Users).filter(Users.username == username).first()
        if not user:
            return False
        if not self.bcrypt_context.verify(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, username: str, user_id: int, role: str, expires_delta: timedelta):
        # Create JWT access token
        encode = {
            'sub': username,
            'id': user_id,
            'role': role,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + expires_delta
        }
        return jwt.encode(encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_bearer)]):
        # Decode and validate JWT token
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
            username = payload.get('sub')
            user_id = payload.get('id')
            user_role = payload.get('role')
            if not isinstance(username, str) or not isinstance(user_id, int):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Could not validate user.'
                )
            return {'username': username, 'id': user_id, 'role': user_role}
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user.'
            )

    # def __call__(self):
    #     print("Hello from a callable class instance!")
