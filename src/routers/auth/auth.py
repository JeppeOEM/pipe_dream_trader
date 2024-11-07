from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from ...database import SessionLocal
from ...models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ...services.auth import AuthenticationService 

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Create a long and random string, use a hex generator
# SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
# ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#tokenUrl is will be send from client to app and hit the auth/token endpoint
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

auth_service = AuthenticationService.AuthService()

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


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
# def authenticate_user(username: str, password: str, db):
#     user = db.query(Users).filter(Users.username == username).first()
#     if not user:
#         return False
#     if not bcrypt_context.verify(password, user.hashed_password):
#         return False
#     return user.model_dump()
#
#
# def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
#     encode = {'sub': username, 'id': user_id, 'role': role}
#     # timestamps aare based on utc
#     expires = datetime.now(timezone.utc) + expires_delta
#     encode.update({'exp': expires})
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
#
#
# # oauth will be injected and extract the jwt
# async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
#     # the payload is from the JWT
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get('sub')
#         user_id = payload.get('id')
#         user_role = payload.get('role')
#         if username is not str or user_id is not int:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail='Could not validate user.')
#         return {'user**/.venv/name': username, 'id': user_id, 'user_role': user_role}
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )

    db.add(create_user_model)
    db.commit()

# response_model vailidates
@router.post("/token", response_model=Token)
# Dependency Injection of the OAuth2PasswordRequestForm
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = auth_service.authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


    token = auth_service.create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}







