from .services.auth.auth_services import hash_password

INITIAL_DATA = {
      'users': [
            {
                  'username': 'superuser',
                  'email': 'superuser@example.com',
                  'hashed_password': hash_password('123')
            },
            {
                  'username': 'admin',
                  'email': 'admin@example.com',
                  'hashed_password': hash_password('123')
            }
      ],
      'sometable': [
            {'column1': 'value', 'column2': 'value'}
      ]
}

def initialize_table(target, connection, **kw):
    tablename = str(target)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])
from fastapi import FastAPI

from .database import engine
from .exceptions import register_all_errors
from .middleware.register_middleware import register_middleware
from .models import Base
from .routers.admin import admin
from .routers.auth import auth
from .routers.strategies import strategies
from .routers.users import users

app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


register_all_errors(app)
# register_middleware(app)

app.include_router(auth.router)
app.include_router(strategies.router)
app.include_router(users.router)
