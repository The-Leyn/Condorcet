import pytest
from flask import Flask
from pymongo import MongoClient
from app.models.scrutin import ScrutinModel

@pytest.fixture(scope="module")
def test_app():
    """Créer une application Flask avec une base de données MongoDB de test."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Connexion à la base de données MongoDB de test
    client = MongoClient("mongodb://localhost:27017")
    app.db = client["test_db"]  # Base de données de test

    yield app

    # Nettoyer après les tests
    client.drop_database("test_db")
    client.close()

@pytest.fixture
def setup_data(test_app):
    """Insérer des données de test dans la base de données."""
    users_collection = test_app.db.users

    # Insérer un utilisateur avec un scrutin
    users_collection.insert_one({
        "username": "user1",
        "scrutin": [
            {
                "scrutin_id": "1",
                "title": "Scrutin 1",
                "description": "Description du scrutin",
                "created_at": "2025-01-01T10:00:00",
                "start_date": "2025-01-02",
                "end_date": "2025-01-10",
                "options": ["Option A", "Option B"],
                "votes": []
            }
        ]
    })

def test_integrity_of_scrutin_data(test_app, setup_data):
    """Tester l'intégrité des données du scrutin après leur insertion dans la base de données."""
    with test_app.app_context():
        # Récupérer le scrutin inséré à partir de la base de données
        scrutin_from_db = test_app.db.users.find_one({
            "username": "user1"
        })["scrutin"][0]

        # Comparer les données
        assert scrutin_from_db["scrutin_id"] == "1"
        assert scrutin_from_db["title"] == "Scrutin 1"
        assert scrutin_from_db["description"] == "Description du scrutin"
        assert scrutin_from_db["created_at"] == "2025-01-01T10:00:00"
        assert scrutin_from_db["start_date"] == "2025-01-02"
        assert scrutin_from_db["end_date"] == "2025-01-10"
        assert scrutin_from_db["options"] == ["Option A", "Option B"]
        assert scrutin_from_db["votes"] == []

