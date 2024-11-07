from passlib.context import CryptContext

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Path
from starlette import status
from ...models import Strategies
from ...exceptions import StrategyNotFound, AuthenticationFailed 
from ...dependencies import user_dependency, db_dependency 

print(user_dependency)
router = APIRouter(tags=['strategy'])

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





class StrategyRequest(BaseModel):
    #model_config allows for assigning directly to the ORM model without type errors
    # model_config = ConfigDict(from_attributes=True)
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    # if user is None:
    #     raise AutheticationFailed()
    return db.query(Strategies).filter(Strategies.owner_id == user.get('id')).all()

@router.get("/strategy/{strategy_id}", status_code=status.HTTP_200_OK)
async def read_strategy(user: user_dependency, db: db_dependency, strategy_id: int = Path(gt=0)):
    # if user is None:
    #     raise AutheticationFailed()

    strategy_model = db.query(Strategies).filter(Strategies.id == strategy_id)\
        .filter(Strategies.owner_id == user.get('id')).first()
    if strategy_model is not None:
        return strategy_model
    #raise StrategyNotFound()
    raise StrategyNotFound()

@router.post("/strategy", status_code=status.HTTP_201_CREATED)
async def create_strategy(user: user_dependency, db: db_dependency,
                      strategy_request: StrategyRequest):
    # if user is None:
    #     raise AutheticationFailed()
    strategy_model = Strategies(**strategy_request.model_dump(), owner_id=user.get('id'))

    db.add(strategy_model)
    db.commit()



@router.put("/strategy/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_strategy(user: user_dependency, db: db_dependency,
                      strategy_request: StrategyRequest,
                      strategy_id: int = Path(gt=0)):
    # Query for the Strategy item to be updated
    strategy_model = db.query(Strategies).filter(Strategies.id == strategy_id)\
        .filter(Strategies.owner_id == user.get('id')).first()
    if strategy_model is None:
        raise StrategyNotFound()

    # Serialize RequestModel into a dict
    data = strategy_request.model_dump()

    for key, value in data.items():
        setattr(strategy_model, key, value)

    db.commit()


# @routertput("/strategy/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_strategy(user: user_dependency, db: db_dependency,
#                       strategy_request: StrategyRequest,
#                       strategy_id: int = Path(gt=0)):
#     # if user is None:
#     #     raise AutheticationFailed()
#
#     strategy_model = db.query(Strategies).filter(Strategies.id == strategy_id)\
#         .filter(Strategies.owner_id == user.get('id')).first()
#     if strategy_model is None:
#         raise StrategyNotFound()
#
#     strategy_model.title = strategy_request.title
#     strategy_model.description = strategy_request.description
#     strategy_model.priority = strategy_request.priority
#     strategy_model.complete = strategy_request.complete
#
#     db.add(strategy_model)
#     db.commit()


@router.delete("/strategy/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(user: user_dependency, db: db_dependency, strategy_id: int = Path(gt=0)):
    # if user is None:
    #     raise AutheticationFailed()

    strategy_model = db.query(Strategies).filter(Strategies.id == strategy_id)\
        .filter(Strategies.owner_id == user.get('id')).first()
    if strategy_model is None:
        raise StrategyNotFound()
    db.query(Strategies).filter(Strategies.id == strategy_id).filter(Strategies.owner_id == user.get('id')).delete()

    db.commit()








