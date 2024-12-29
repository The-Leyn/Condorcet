from flask import current_app
from bson import ObjectId
import hashlib

class UserModel:
    @staticmethod
    def find_by_id_user(id_user):
        object_id = ObjectId(id_user)
        """Trouver un utilisateur par son nom d'utilisateur."""
        user = current_app.db.users.find_one({"_id": object_id})
        return user
    
    @staticmethod
    def find_all_user():
        """Trouver tout les utilisateurs."""
        users = list(current_app.db.users.find())
        return users

    @staticmethod
    def create_user(data):
        """Créer un nouvel utilisateur."""
        result = current_app.db.users.insert_one(data)
        return result.inserted_id
    
    @staticmethod
    def find_by_email(email):
        """Trouver un utilisateur par son addresse email"""
        user = current_app.db.users.find_one({"email": email})
        return user
    
    @staticmethod
    def verify_password(input_password, stored_password_hash):
        """Vérifie si le mot de passe correspond au hachage."""
        hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
        return hashed_input == stored_password_hash
    
    @staticmethod
    def login(email, password):
        """
        Connecte un utilisateur via son email et mot de passe.
        Retourne l'utilisateur si les identifiants sont corrects.
        """
        user = UserModel.find_by_email(email)
        if not user:
            return {"error": "Utilisateur introuvable."}, False

        # Vérification du mot de passe
        if UserModel.verify_password(password, user["password_hash"]):
            return {"message": "Connexion réussie.", "user": user}, True
        else:
            return {"error": "Mot de passe incorrect."}, False