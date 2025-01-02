from flask import current_app
from bson import ObjectId

class ScrutinModel:
    @staticmethod
    def find_scrutins():
        """Trouver tous les scrutins pour tous les utilisateurs."""
        users = list(current_app.db.users.find())
        scrutins = []
        for user in users:
            if 'scrutin' in user:
                for scrutin in user['scrutin']:
                    scrutin['user'] = f"{user['firstname']} {user['lastname']}"  # Associer l'utilisateur
                    scrutins.append(scrutin)
        return scrutins

    @staticmethod
    def find_scrutins_by_user(user_id):
        """Trouver les scrutins d'un utilisateur spécifique."""
        object_id = ObjectId(user_id)
        user = current_app.db.users.find_one({"_id": object_id})
        if user and 'scrutin' in user:
            return user['scrutin']
        return []

    @staticmethod
    def create_scrutin(user_id, scrutin_data):
        """Ajouter un scrutin pour un utilisateur spécifique."""
        object_id = ObjectId(user_id)
        current_app.db.users.update_one(
            {"_id": object_id},
            {"$push": {"scrutin": scrutin_data}}
        )
