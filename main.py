from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers.auth import auth
from .routers.strategies import strategies
from .routers.admin import admin
from .routers.users import users
from .exceptions import register_all_errors
from .middleware.register_middleware import register_middleware 

app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}

register_all_errors(app)
register_middleware(app)

app.include_router(auth.router)
app.include_router(strategies.router)
app.include_router(admin.router)
app.include_router(users.router)
