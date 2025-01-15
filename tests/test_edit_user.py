import pytest
from flask import session
from bson import ObjectId
from app import create_app  # Utilisez votre fonction de création d'app Flask
from app.models.user import UserModel
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app = create_app()  # Créez votre app Flask avec la configuration appropriée
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    app.config["DATABASE_URI"] = "mongodb://localhost:27017/test"  # URI pour la DB de test
    with app.test_client() as client:
        with app.app_context():  # Assurez-vous que l'application est dans le contexte
            # Initialisation de la base de données ou autres préparations nécessaires
            pass
        yield client


@pytest.fixture
def create_user():
    """Fixture pour créer un utilisateur pour les tests"""
    def _create_user(email, pseudonym, firstname, lastname, password):
        user_data = {
            "email": email,
            "pseudonym": pseudonym,
            "firstname": firstname,
            "lastname": lastname,
            "password_hash": generate_password_hash(password),
            "is_active": True,
            "role": "user"
        }
        return UserModel.create_user(user_data)
    return _create_user

def test_edit_user_success(client, create_user):
    """Test si l'utilisateur met à jour son profil avec succès"""
    # Créer un utilisateur et se connecter dans le contexte de l'application
    with client.application.app_context():  # Crée un contexte d'application ici
        user_id = create_user("test@example.com", "testuser", "John", "Doe", "password123")

    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})

    # Effectuer la mise à jour du profil
    response = client.post("/edit-profile", data={
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'newemail@example.com'
    })

    # Vérification de la redirection vers la page de profil
    assert response.status_code == 302  # Redirection après mise à jour réussie
    assert response.location.endswith("/profile")  # Vérification que la redirection mène à la page de profil

    # Suivi de la redirection pour vérifier le profil mis à jour
    follow_response = client.get(response.location)  # Suivi de la redirection
    assert follow_response.status_code == 200  # Vérification que la page est bien chargée
    assert b"Jane" in follow_response.data  # Vérification du prénom mis à jour
    assert b"Smith" in follow_response.data  # Vérification du nom mis à jour
    assert b"newemail@example.com" in follow_response.data  # Vérification de l'email mis à jour


def test_edit_user_not_logged_in(client):
    """Test si l'utilisateur est redirigé vers la page de connexion quand il n'est pas connecté"""
    response = client.get("/edit-profile")
    assert response.status_code == 302  # Redirection vers la page de connexion
    assert b"login" in response.data  # Vérifier si la redirection est vers la page de login


def test_edit_user_not_found(client):
    """Test si un utilisateur n'existe pas"""
    # Simuler un utilisateur connecté avec un ID non valide    
    invalid_user_id = str(ObjectId())  # Génère un ObjectId valide mais inexistant dans la DB

    with client.session_transaction() as sess:
        sess['user_id'] = invalid_user_id  # Utilisateur inexistant avec un ID valide

    response = client.get("/edit-profile")
    
    # Vérification que l'ID utilisateur inexistant entraîne une erreur 404
    assert response.status_code == 404  # Utilisateur non trouvé


def test_edit_user_missing_fields(client, create_user):
    """Test si l'utilisateur soumet un formulaire avec des champs manquants"""
    with client.application.app_context():  # Crée un contexte d'application ici
        user_id = create_user("test@example.com", "testuser", "John", "Doe", "password123")

    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})

    # Effectuer la mise à jour du profil avec des champs manquants
    response = client.post("/edit-profile", data={
        'firstname': '',  # Champs manquant
        'lastname': 'Smith',
        'email': ''  # Champs manquants
    })

    # Vérification de la réponse
    assert response.status_code == 400  # Le code de statut attendu est 400


def test_edit_user_invalid_email(client, create_user):
    """Test si l'utilisateur soumet un email invalide"""
    with client.application.app_context():  # Crée un contexte d'application ici
        user_id = create_user("test@example.com", "testuser", "John", "Doe", "password123")
    
    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})
    
    # Effectuer la mise à jour du profil avec un email invalide
    response = client.post("/edit-profile", data={
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'invalid-email'
    })
    
    # Vérification que l'email invalide est rejeté
    assert b"Adresse e-mail invalide" in response.data


def test_edit_user_update_failure(client, create_user, mocker):
    """Test si une erreur se produit lors de la mise à jour de l'utilisateur"""

    # Créer un utilisateur dans un contexte d'application
    with client.application.app_context():
        user_id = create_user("test@example.com", "testuser", "John", "Doe", "password123")

    client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})

    # Mocking a failure in the update process
    mocker.patch('app.models.user.UserModel.update_user', side_effect=Exception("Erreur lors de la mise à jour"))

    # Effectuer la requête de mise à jour du profil
    response = client.post("/edit-profile", data={
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'newemail@example.com'
    })

    # Vérification du code de redirection (302) et de l'URL de redirection
    assert response.status_code == 302
    assert response.location == '/edit-profile'  # Vérifiez si la redirection va vers la page correcte

    # Effectuer une autre requête pour accéder à la page après la redirection et vérifier l'erreur
    redirected_response = client.get('/edit-profile')
    assert "Erreur lors de la mise à jour" in redirected_response.data.decode('utf-8')