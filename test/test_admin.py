from .utils import *
from ..routers.admin import get_db, get_current_user
from fastapi import status
from ..models import Strategies

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_read_all_authenticated(test_strategy):
    response = client.get("/admin/strategy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_admin_delete_strategy(test_strategy):
    response = client.delete("/admin/strategy/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Strategies).filter(Strategies.id == 1).first()
    assert model is None


def test_admin_delete_strategy_not_found():
    response = client.delete("/admin/strategy/9999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Strategy not found.'}










