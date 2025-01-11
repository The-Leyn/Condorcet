import pytest
from flask import session
from app import create_app  # Suppose que ton application Flask est initialisée dans un fichier app.py


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_register_post_missing_fields(client):
    """Test si un message d'erreur s'affiche quand des champs sont manquants."""
    response = client.post('/register', data={
        'email': '',
        'password': '',
        'pseudonym': '',
        'firstname': '',
        'lastname': '',
        'repeatpassword': '',
    })
    assert response.status_code == 200
    assert b"Veuillez remplir tous les champs." in response.data


def test_register_passwords_dont_match(client):
    """Test si un message d'erreur s'affiche quand les mots de passe ne correspondent pas."""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'pseudonym': 'testuser',
        'firstname': 'John',
        'lastname': 'Doe',
        'repeatpassword': 'differentpassword',
    })
    assert response.status_code == 200
    assert b"Les mots de passe ne correspondent pas." in response.data
