from flask import current_app, session
from bson import ObjectId
from werkzeug.security import check_password_hash



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
        """Trouve un utilisateur par son email."""
        return current_app.db.users.find_one({"email": email})

# CONNEXION

    @staticmethod
    def login(email, password):
        """Vérifie les informations d'identification et crée une session."""
        user = UserModel.find_by_email(email)
        if not user:
            return {"error": "Utilisateur introuvable."}, False

        if check_password_hash(user["password_hash"], password):
            session['user_id'] = str(user.get('_id'))
            session['user_email'] = user.get('email')
            session['user_pseudonym'] = user.get('pseudonym')
            session['user_firstname'] = user.get('firstname')
            session['user_lastname'] = user.get('lastname')
            session['user_role'] = user.get('role')
            return {"message": "Connexion réussie.", "user": user}, True
        else:
            return {"error": "Mot de passe incorrect."}, False

# DÉCONNEXION
    @staticmethod
    def logout():
        """Déconnecte l'utilisateur."""
        session.clear()
        return {"message": "Déconnexion réussie."}