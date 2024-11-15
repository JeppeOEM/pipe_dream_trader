import pytest
from fastapi import status
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..dependencies import get_db
from ..main import app
from ..models import Strategies, Users
from ..services.auth.auth_services import get_current_user

client = TestClient(app)

headers = {"Host": "localhost"}


def mock_get_current_user():
    # Return a mock authenticated user
    return {'username': 'codingwithrobytest', 'id': 1, 'user_role': 'admin'}


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

TEST_DB="postgresql://user:pass@db:5432/db"

testengine = create_engine(
    TEST_DB
)

# create seperate database session for testing
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testengine)

Base.metadata.create_all(bind=testengine)


def mock_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the real dependency with the mock
app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db] = mock_get_db


@pytest.fixture
def test_strategy():
    # Create a strategy object for testing
    strategy = Strategies(
        title="Learn to code!",
        description="Need to learn everyday!",
        fk_user_id=1,  # Link to test user
    )
    # Use the testing session to add the strategy to the database
    db = TestingSessionLocal()
    db.add(strategy)
    db.commit()
    yield strategy  # Yield the strategy object for the test to use
    # Cleanup: delete the strategy after the test
    with testengine.connect() as connection:
        connection.execute(text("DELETE FROM strategy;"))
        connection.commit()


@pytest.fixture
def test_user():
    # Create a test user for authentication testing
    user = Users(
        username="jeppe",
        email="jeppe@email.com",
        first_name="jeppe",
        last_name="jeppesen",
        hashed_password=bcrypt_context.hash("testpassword"),  # Hashed password
        role="admin",
    )
    # Add the user to the database using the testing session
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user  # Yield the user object for the test to use
    # Cleanup: delete the user after the test
    with testengine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


def check_user_exists(db: Session, user_id: int) -> bool:
    return db.query(Users).filter(Users.id == user_id).first() is not None


def test_check_fixure_user_exists(test_user):
    db = TestingSessionLocal()  
    user_exists = check_user_exists(
        db, test_user.id
    )  
    db.close()  

    assert user_exists is True
#


def test_allowed_host():
    response = client.get("/healthy", headers={"Host": "localhost"})
    assert response.status_code == 200


def test_disallowed_host():
    response = client.get("/healthy", headers={"Host": "malicious.com"})
    assert response.status_code == 400


def test_read_all_authenticated():
    response = client.get("/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
