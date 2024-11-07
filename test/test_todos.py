from ..routers.strategies import get_db, get_current_user
from fastapi import status
from ..models import Strategies
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_strategy):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_read_one_authenticated(test_strategy):
    response = client.get("/strategy/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}


def test_read_one_authenticated_not_found():
    response = client.get("/strategy/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Strategy not found.'}


def test_create_strategy(test_strategy):
    request_data={
        'title': 'New Strategy!',
        'description':'New strategy description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/strategy/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Strategies).filter(Strategies.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_strategy(test_strategy):
    request_data={
        'title':'Change the title of the strategy already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/strategy/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Strategies).filter(Strategies.id == 1).first()
    assert model.title == 'Change the title of the strategy already saved!'


def test_update_strategy_not_found(test_strategy):
    request_data={
        'title':'Change the title of the strategy already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/strategy/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Strategy not found.'}


def test_delete_strategy(test_strategy):
    response = client.delete('/strategy/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Strategies).filter(Strategies.id == 1).first()
    assert model is None


def test_delete_strategy_not_found():
    response = client.delete('/strategy/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Strategy not found.'}













