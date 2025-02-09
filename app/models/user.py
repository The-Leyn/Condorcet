from flask import current_app, session
from bson import ObjectId
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

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
    
    @staticmethod
    def find_by_pseudonym(pseudonym):
        """Trouve un utilisateur pas son pseudonym"""
        return current_app.db.users.find_one({"pseudonym": pseudonym})


# CONNEXION
    @staticmethod
    def login(email, password):
        """Vérifie si les champs ne sont pas vide"""
        if not email or not password:
            return {"error" : "Email ou mot de passe vide"}, False

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
    
#INSCRIPTION    
    @staticmethod
    def register(user_data):
        email = user_data["email"]
        pseudonym = user_data["pseudonym"]

        # Vérifie si un utilisateur existe
        existing_user = current_app.db.users.find_one({
            "$or": [{"email": email}, {"pseudonym": pseudonym}]
        })

        if existing_user:
            raise ValueError("L'email ou le pseudonyme est déjà utilisé.")

        # Hache le mot de passe
        user_data["password_hash"] = generate_password_hash(user_data["password_hash"])
        result = current_app.db.users.insert_one(user_data)
        return result.inserted_id
    
    @staticmethod
    def deactivate_user(user_id):
        """Désactive un utilisateur en supprimant les champs inutiles, sauf 'scrutins', 'pseudonym' et en mettant 'is_active' à False."""
        # Récupérer l'utilisateur actuel pour identifier les champs existants
        user = current_app.db.users.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise ValueError("Utilisateur introuvable")

        # Identifier les champs à supprimer
        fields_to_keep = {"_id", "scrutin", "pseudonym", "is_active"}
        fields_to_remove = {key: "" for key in user if key not in fields_to_keep}

        # Mettre à jour l'utilisateur
        result = current_app.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$unset": fields_to_remove,  # Supprimer les champs non essentiels
                "$set": {
                    "is_active": False  # Désactiver l'utilisateur
                }
            }
        )
        return result.modified_count > 0  # Retourne True si la mise à jour a été effectuée
    
# MODIFICATION
    @staticmethod
    def update_user(user_id, updated_data):
        """Met à jour les informations d'un utilisateur."""
        object_id = ObjectId(user_id)
        
        # Vérifie si l'utilisateur existe
        user = current_app.db.users.find_one({"_id": object_id})
        if not user:
            raise ValueError("Utilisateur non trouvé.")

        # Met à jour les champs dans la base de données
        current_app.db.users.update_one(
            {"_id": object_id},  # Filtre : utilisateur à mettre à jour
            {"$set": updated_data}  # Mises à jour à appliquer
        )

    @staticmethod
    def count_users():
        """Compter le nombre total d'utilisateurs inscrits."""
        return current_app.db.users.count_documents({})
    # print(UserModel.count_users())

    @staticmethod
    def count_active_users():
        """Compter le nombre total d'utilisateurs actifs."""
        return current_app.db.users.count_documents({"is_active": True})
    