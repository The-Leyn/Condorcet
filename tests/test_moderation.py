import pytest
from unittest.mock import patch
from bson.objectid import ObjectId
from app.models.scrutin import ScrutinModel
from app import create_app 

@pytest.fixture
def app_context():
    app = create_app() 
    with app.app_context():
        yield app


@patch('app.models.scrutin.current_app.db.users.find_one')
def test_disable_scrutin_unauthorized(mock_find_one, app_context):
    # Simulate non-admin user
    unauthorized_user = {'_id': ObjectId(), 'role': 'user'}
    mock_find_one.return_value = unauthorized_user

    scrutin_id = ObjectId()
    response = ScrutinModel.disableScrutinAsAdmin(scrutin_id, unauthorized_user['_id'])

    assert response['success'] is False
    assert response['message'] == "Accès refusé. Seuls les administrateurs peuvent désactiver les scrutins."
