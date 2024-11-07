from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from ...models import Users
from fastapi.security import OAuth2PasswordRequestForm
from ...services.auth import AuthenticationService, PasswordService
from ...dependencies import db_dependency
from .schemas import *

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

auth_service = AuthenticationService.AuthService()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=PasswordService.hash_password(create_user_request.password),
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







