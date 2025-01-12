import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import check_password_hash
from app.models.user import UserModel

# Similution d'une session et d'une base de donnée temporaire pour les tests
@patch('app.models.user.UserModel.find_by_email')
@patch('app.models.user.session', new_callable=dict)
def test_login_user_not_found(mock_session, mock_find_by_email):
    # Simulate user not found
    mock_find_by_email.return_value = None
    
    response, success = UserModel.login('test@example.com', 'password123')
    
    assert not success
    assert response == {"error": "Utilisateur introuvable."}

