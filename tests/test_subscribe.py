import pytest
import re
from flask import Flask, session
from app import create_app  # Suppose que ton application Flask est initialisée dans un fichier app.py
from app.models.user import UserModel

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

import html

def test_register_email_or_pseudonym_exists(client, mocker):
    # Simule que l'email est déjà pris
    mocker.patch("app.models.user.UserModel.find_by_email", return_value=True)    
    mocker.patch("app.models.user.UserModel.find_by_pseudonym", return_value=False)

    data = {
        "email": "existing@example.com",
        "pseudonym": "newuser",
        "firstname": "Existing",
        "lastname": "User",
        "password": "password123",
        "repeatpassword": "password123"
    }

    response = client.post("/register", data=data)

    # Vérification que la page de registre a été rendue avec un message d'erreur  
    assert response.status_code == 200

    # Décoder la réponse en texte pour pouvoir la comparer avec une chaîne de caractères
    response_data_str = response.data.decode('utf-8')

    # Décoder les entités HTML
    decoded_response_data = html.unescape(response_data_str)

    # Vérification du message d'erreur
    assert "L'email est déjà utilisé." in decoded_response_data

def test_register_success(client, mocker):
    # Patch pour éviter d'interagir avec la base de données
    mocker.patch("app.models.user.UserModel.find_by_email", return_value=None)
    
    data = {
        "email": "new@example.com",
        "pseudonym": "newuser",
        "firstname": "New",
        "lastname": "User",
        "password": "password123",
        "repeatpassword": "password123"
    }
    
    response = client.post("/register", data=data)

def test_register_redirect_if_logged_in(client):
    # Simuler un utilisateur connecté
    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.get("/register", follow_redirects=False)

    # Vérification de la redirection vers la racine
    assert response.status_code == 302  # Redirection vers la page d'accueil
    assert response.location.endswith('/')  # Vérification de la redirection vers la racine

def test_register_invalid_email(client):
    data = {
        "email": "invalid-email",
        "pseudonym": "user",
        "firstname": "Invalid",
        "lastname": "User",
        "password": "password123",
        "repeatpassword": "password123"
    }

    response = client.post("/register", data=data)

    # Décoder la réponse en texte pour pouvoir la comparer avec une chaîne de caractères
    response_data_str = response.data.decode('utf-8')

    # Debug : afficher la réponse complète pour vérifier le contenu
    print(response_data_str)

    # Vérification du code de statut
    assert response.status_code == 200

    # Vérification que le message d'erreur de l'email invalide est présent dans la réponse
    assert "Adresse e-mail invalide" in response_data_str

    