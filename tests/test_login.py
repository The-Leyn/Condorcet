import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
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

@patch('app.models.user.UserModel.find_by_email')
@patch('app.models.user.session', new_callable=dict)
def test_login_wrong_password(mock_session, mock_find_by_email):
    # Simulate found user with wrong password
    user_data = {
        'password_hash': generate_password_hash('correct_password')
    }
    mock_find_by_email.return_value = user_data
    
    response, success = UserModel.login('test@example.com', 'wrong_password')
    
    assert not success
    assert response == {"error": "Mot de passe incorrect."}

@patch('app.models.user.UserModel.find_by_email')
@patch('app.models.user.session', new_callable=dict)
def test_login_success(mock_session, mock_find_by_email):
    # Simulate found user with correct password
    user_data = {
        '_id': 1,
        'email': 'test@example.com',
        'pseudonym': 'testuser',
        'firstname': 'Test',
        'lastname': 'User',
        'role': 'user',
        'password_hash': generate_password_hash('correct_password')
    }
    mock_find_by_email.return_value = user_data
    
    response, success = UserModel.login('test@example.com', 'correct_password')
    
    assert success
    assert response["message"] == "Connexion réussie."
    assert response["user"] == user_data
    assert mock_session['user_id'] == str(user_data['_id'])

@patch('app.models.user.UserModel.find_by_email')
@patch('app.models.user.session', new_callable=dict)
def test_login_empty_email_or_password(mock_session, mock_find_by_email) :
    # simulate empty email
    mock_find_by_email.return_value = None

    response, success = UserModel.login('', 'password123')
    response, success = UserModel.login('example@email.com','')

    assert not success
    assert response == {"error": "Email ou mot de passe vide"}