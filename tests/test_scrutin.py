import pytest
from flask import Flask, current_app
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Fonction de création d'un scrutin 
def create_scrutin(db, user_id, title, description, start_date, end_date, options):
    """Fonction pour créer un scrutin pour un utilisateur spécifique."""
    scrutin = {
        "scrutin_id": ObjectId(),
        "created_at": datetime.now(),
        "is_active": True,
        "title": title,
        "description": description,
        "start_date": datetime.strptime(start_date, "%Y-%m-%dT%H:%M"),
        "end_date": datetime.strptime(end_date, "%Y-%m-%dT%H:%M"),
        "options": options,
        "votes": []
    }

    # Ajouter le scrutin dans le tableau des scrutins de l'utilisateur
    db.users.update_one(
        {"_id": user_id},
        {"$push": {"scrutin": scrutin}}
    )

    return scrutin  # Retourner le scrutin ajouté pour vérification

@pytest.fixture(scope="module")
def test_app():
    """Créer une application Flask connectée à la base de données MongoDB réelle."""
    app = Flask(__name__)
    app.config['TESTING'] = True

    # Connexion à votre base de données MongoDB réelle
    client = MongoClient("mongodb://localhost:27017")
    app.db = client["condorcet"]  # Nom de votre base de données réelle

    yield app

    # Fermeture du client après les tests
    client.close()


@pytest.fixture
def setup_data(test_app):
    """Insérer des données de test dans la base de données réelle."""
    users_collection = test_app.db.users

    # Préparer les scrutins de test
    test_scrutins = [
        {
            "scrutin_id": ObjectId(),
            "created_at": datetime.now(),
            "is_active": True,
            "title": f"Scrutin Test {i}",
            "description": f"Description pour le scrutin test {i}",
            "start_date": datetime(2025, 1, i + 1, 10, 0),
            "end_date": datetime(2025, 1, i + 2, 18, 0),
            "options": [f"Option {chr(65+j)}" for j in range(3)],
            "votes": []
        }
        for i in range(2)
    ]

    # Ajouter un utilisateur de test avec des scrutins de test
    test_user = {
        "_id": ObjectId(),
        "pseudonym": "test_user",
        "firstname": "Test",
        "lastname": "User",
        "email": "test_user@email.com",
        "password_hash": "hashed_password",
        "is_active": True,
        "role": "user",
        "scrutin": test_scrutins
    }

    # Insérer l'utilisateur de test
    users_collection.insert_one(test_user)

    yield test_scrutins, test_user["_id"]

    # Nettoyer après les tests
    users_collection.delete_one({"_id": test_user["_id"]})


def test_integrity_of_scrutin_data(test_app, setup_data):
    """Tester l'intégrité des données du scrutin après leur insertion dans la base de données."""
    scrutins_inserted, user_id = setup_data

    with test_app.app_context():
        # Récupérer l'utilisateur inséré
        user_from_db = test_app.db.users.find_one({"_id": user_id})
        assert user_from_db is not None, "L'utilisateur de test n'a pas été inséré correctement."

        # Récupérer les scrutins associés
        scrutins_from_db = user_from_db["scrutin"]
        assert len(scrutins_from_db) == len(scrutins_inserted), "Le nombre de scrutins ne correspond pas."

        # Vérifier que chaque scrutin correspond
        for scrutin_inserted in scrutins_inserted:
            assert any(
                scrutin_inserted["scrutin_id"] == scrutin_from_db["scrutin_id"]
                for scrutin_from_db in scrutins_from_db
            ), f"Le scrutin {scrutin_inserted['title']} n'a pas été trouvé dans la base de données."


def test_create_scrutin_for_all_users(test_app):
    """Tester l'ajout d'un scrutin pour tous les utilisateurs."""
    with test_app.app_context():
        db = test_app.db
        users_collection = db.users

        # Préparer les données du scrutin
        title = "Test Scrutin"
        description = "Description pour un test global."
        start_date = "2025-01-15T10:00"
        end_date = "2025-01-20T18:00"
        options = ["Option A", "Option B", "Option C"]

        # Créer un scrutin et l'ajouter pour chaque utilisateur
        new_scrutin = {
            "scrutin_id": ObjectId(),
            "created_at": datetime.now(),
            "is_active": True,
            "title": title,
            "description": description,
            "start_date": datetime.strptime(start_date, "%Y-%m-%dT%H:%M"),
            "end_date": datetime.strptime(end_date, "%Y-%m-%dT%H:%M"),
            "options": options,
            "votes": []
        }

        # Ajouter le scrutin pour tous les utilisateurs
        users_collection.update_many(
            {},
            {"$push": {"scrutin": new_scrutin}}
        )

        # Vérifier que le scrutin a été ajouté à tous les utilisateurs
        for user in users_collection.find({}):
            assert any(
                s["title"] == title and s["description"] == description
                for s in user.get("scrutin", []))
        
        # Nettoyer les scrutins de test
        users_collection.update_many(
            {},
            {"$pull": {"scrutin": {"title": title}}}
        )

        # Vérifier que le nettoyage a été effectué
        for user in users_collection.find({}):
            assert not any(
                s["title"] == title for s in user.get("scrutin", []))


def test_edit_scrutin(test_app, setup_data):
    """Tester la modification d'un scrutin pour un utilisateur spécifique."""
    scrutins_inserted, user_id = setup_data

    # Sélectionner un scrutin à modifier
    scrutin_to_edit = scrutins_inserted[0]
    scrutin_id = scrutin_to_edit["scrutin_id"]

    # Préparer les nouvelles données pour la modification
    new_title = "Scrutin Modifié"
    new_description = "Description modifiée du scrutin."
    new_start_date = "2025-01-16T10:00"
    new_end_date = "2025-01-21T18:00"
    new_options = ["Option X", "Option Y", "Option Z"]

    with test_app.app_context():
        # Appeler la fonction de mise à jour du scrutin
        result = current_app.db.users.update_one(
            {"_id": ObjectId(user_id), "scrutin.scrutin_id": scrutin_id},
            {"$set": {
                "scrutin.$.title": new_title,
                "scrutin.$.description": new_description,
                "scrutin.$.start_date": datetime.strptime(new_start_date, "%Y-%m-%dT%H:%M"),
                "scrutin.$.end_date": datetime.strptime(new_end_date, "%Y-%m-%dT%H:%M"),
                "scrutin.$.options": new_options
            }}
        )

        # Vérifier que le scrutin a bien été mis à jour
        assert result.matched_count > 0, f"Aucun scrutin trouvé avec l'id {scrutin_id}."
        assert result.modified_count > 0, f"Le scrutin {scrutin_id} n'a pas été modifié."

        # Récupérer l'utilisateur et le scrutin modifié
        user_from_db = test_app.db.users.find_one({"_id": user_id})
        updated_scrutin = next((s for s in user_from_db["scrutin"] if str(s["scrutin_id"]) == str(scrutin_id)), None)

        # Vérifier que les nouvelles données sont bien enregistrées
        assert updated_scrutin is not None, "Le scrutin n'a pas été trouvé après la modification."
        assert updated_scrutin["title"] == new_title, "Le titre n'a pas été mis à jour correctement."
        assert updated_scrutin["description"] == new_description, "La description n'a pas été mise à jour correctement."
        assert updated_scrutin["start_date"] == datetime.strptime(new_start_date, "%Y-%m-%dT%H:%M"), "La date de début n'a pas été mise à jour correctement."
        assert updated_scrutin["end_date"] == datetime.strptime(new_end_date, "%Y-%m-%dT%H:%M"), "La date de fin n'a pas été mise à jour correctement."
        assert updated_scrutin["options"] == new_options, "Les options n'ont pas été mises à jour correctement."
