from flask import current_app
from datetime import datetime
class ScrutinModel:
    @staticmethod
    def find_10_last():
        """Récupérer les 10 derniers scrutins."""
        scrutins = list(
            current_app.db.users.aggregate([
                {"$unwind": "$scrutin"},  # $unwind Permet de transformer chaque élément du tableau scrutin en un document distinct. Donc chaque scrutin est traité individuellement.
                {"$sort": {"scrutin.created_at": -1}},  # Trier par date de création décroissante
                {"$limit": 10},  # Limiter à 10 résultats
                {"$project": {  # Sélectionner uniquement les champs nécessaires
                    "_id": 0,
                    "question_id": "$scrutin.question_id",
                    "title": "$scrutin.title",
                    "description": "$scrutin.description",
                    "created_at": "$scrutin.created_at",
                    "start_date": "$scrutin.start_date",
                    "end_date": "$scrutin.end_date",
                    "options": "$scrutin.options",
                    "votes": "$scrutin.votes"
                }}
            ])
        )
        return scrutins
    
    def find_10_last_active():
        """Récupérer les 10 derniers scrutins actif."""
        now = datetime.today()
        scrutins = list(
            current_app.db.users.aggregate([
                {"$unwind": "$scrutin"},  # $unwind Permet de transformer chaque élément du tableau scrutin en un document distinct. Donc chaque scrutin est traité individuellement.
                {"$match": {"scrutin.end_date": {"$lt": now}}},
                {"$sort": {"scrutin.created_at": -1 }},  # Trier par date de création décroissante
                {"$limit": 10},  # Limiter à 10 résultats
                {"$project": {  # Sélectionner uniquement les champs nécessaires
                    "_id": 0,
                    "question_id": "$scrutin.question_id",
                    "title": "$scrutin.title",
                    "description": "$scrutin.description",
                    "created_at": "$scrutin.created_at",
                    "start_date": "$scrutin.start_date",
                    "end_date": "$scrutin.end_date",
                    "options": "$scrutin.options",
                    "votes": "$scrutin.votes"
                }}
            ])
        )
        return scrutins
        