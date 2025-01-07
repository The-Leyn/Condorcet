from flask import current_app
from bson import ObjectId

class UserModel:
    @staticmethod
    def find_by_id_user(id_user):
        object_id = ObjectId(id_user)
        """Trouver un utilisateur par son nom d'utilisateur."""
        user = current_app.db.users.find_one({"_id": object_id})
        return user
    
    def find_all_user():
        """Trouver tout les utilisateurs."""
        users = list(current_app.db.users.find())
        return users

    @staticmethod
    def create_user(data):
        """Créer un nouvel utilisateur."""
        result = current_app.db.users.insert_one(data)
        return result.inserted_id