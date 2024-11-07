from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./strategiesapp.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

#SQLAlchemy will create the tables
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#any SQLAlchemy model will inherit from this base class
Base = declarative_base()
