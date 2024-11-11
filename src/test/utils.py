# from sqlalchemy import create_engine, text
# from sqlalchemy.pool import StaticPool
# from sqlalchemy.orm import sessionmaker
# from ..database import Base
# from ..main import app
# from fastapi.testclient import TestClient
# import pytest
# from ..models import Strategies, Users
# from passlib.context import CryptContext
#
# bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass = StaticPool,
# )
#
# # create seperate database session for testing
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base.metadata.create_all(bind=engine)
#
# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# def override_get_current_user():
#     return {'username': 'codingwithrobytest', 'id': 1, 'user_role': 'admin'}
#
# client = TestClient(app)
#
# @pytest.fixture
# def test_strategy():
#     strategy = Strategies(
#         title="Learn to code!",
#         description="Need to learn everyday!",
#         priority=5,
#         complete=False,
#         owner_id=1,
#     )
#
#     db = TestingSessionLocal()
#     db.add(strategy)
#     db.commit()
#     yield strategy
#     with engine.connect() as connection:
#         connection.execute(text("DELETE FROM strategy;"))
#         connection.commit()
#
#
# @pytest.fixture
# def test_user():
#     user = Users(
#         username="codingwithrobytest",
#         email="codingwithrobytest@email.com",
#         first_name="Eric",
#         last_name="Roby",
#         hashed_password=bcrypt_context.hash("testpassword"),
#         role="admin",
#         phone_number="(111)-111-1111"
#     )
#     db = TestingSessionLocal()
#     db.add(user)
#     db.commit()
#     yield user
#     with engine.connect() as connection:
#         connection.execute(text("DELETE FROM users;"))
#         connection.commit()
#
#
#
#
#
#
