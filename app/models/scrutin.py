from flask import current_app
from datetime import datetime
from bson.objectid import ObjectId
class ScrutinModel:
    @staticmethod
    def find_10_last():
        """Récupérer les 10 derniers scrutins."""
        scrutins = list(
            current_app.db.users.aggregate([
                {"$unwind": "$scrutin"},  # $unwind Permet de transformer chaque élément du tableau scrutin en un document distinct. Donc chaque scrutin est traité individuellement.
                {"$match": {"scrutin.is_active": True}},
                {"$sort": {"scrutin.created_at": -1}},  # Trier par date de création décroissante
                {"$limit": 10},  # Limiter à 10 résultats
                {"$project": {  # Sélectionner uniquement les champs nécessaires
                    "_id": 0,
                    "scrutin_id": "$scrutin.scrutin_id",
                    "title": "$scrutin.title",
                    "description": "$scrutin.description",
                    "created_at": "$scrutin.created_at",
                    "is_active": "$scrutin.is_active",
                    "start_date": "$scrutin.start_date",
                    "end_date": "$scrutin.end_date",
                    "options": "$scrutin.options",
                    "votes": "$scrutin.votes"
                }}
            ])
        )
        return scrutins
    
    @staticmethod
    def find_10_last_active():
        """Récupérer les 10 derniers scrutins actifs distincts (avec des votes récents)."""
        scrutins = list(
            current_app.db.users.aggregate([
                {"$unwind": "$scrutin"},
                {"$match": {"scrutin.is_active": True}},
                {"$unwind": "$scrutin.votes"},
                {"$sort": {"scrutin.votes.created_at": -1}},
                {"$group": {  # Grouper par scrutin_id pour obtenir des scrutins uniques
                    "_id": "$scrutin.scrutin_id",  # Grouper par identifiant de scrutin
                    "title": {"$first": "$scrutin.title"},
                    "description": {"$first": "$scrutin.description"},
                    "created_at": {"$first": "$scrutin.created_at"},
                    "is_active": {"$first": "$scrutin.is_active"},
                    "start_date": {"$first": "$scrutin.start_date"},
                    "end_date": {"$first": "$scrutin.end_date"},
                    "options": {"$first": "$scrutin.options"},
                    "last_vote_date": {"$max": "$scrutin.votes.created_at"},  # Dernière date de vote
                }},
                {"$sort": {"last_vote_date": -1}},  # Trier par date du dernier vote
                {"$limit": 10}
            ])
        )
        return scrutins

    
    @staticmethod
    def find_created_by_user(user_id):
        """Récupérer les scrutins créés par un utilisateur"""
        scrutins = list(
            current_app.db.users.aggregate([ 
                { "$match": { "_id": ObjectId(user_id) }},
                { "$unwind": "$scrutin" }, 
                { "$sort": { "scrutin.created_at": -1 }}, 
                {"$project": {
                    "_id": 0,
                    "scrutin_id": "$scrutin.scrutin_id",
                    "title": "$scrutin.title", 
                    "description": "$scrutin.description", 
                    "created_at": "$scrutin.created_at",
                    "is_active": "$scrutin.is_active",
                    "start_date": "$scrutin.start_date", 
                    "end_date": "$scrutin.end_date", 
                    "options": "$scrutin.options", 
                    "votes": "$scrutin.votes"
                }}
            ])
        )
        return scrutins

    @staticmethod
    def find_user_participations(user_id):
        """Récupérer les scrutins auquel l'utilisateur à participé"""
        scrutins = list(
            current_app.db.users.aggregate([
                {"$unwind": "$scrutin"},  # Décompose chaque scrutin
                {"$unwind": "$scrutin.votes"},  # Décompose chaque vote dans les scrutins
                {"$match": {
                    "scrutin.votes.voter_id": ObjectId(user_id),
                    "scrutin.is_active": True}
                },
                {"$sort": {"scrutin.created_at": -1}},  # Trier par date de création décroissante
                {"$project": {  # Sélectionner les champs nécessaires
                    "_id": 0,
                    "scrutin_id": "$scrutin.scrutin_id",
                    "title": "$scrutin.title",
                    "description": "$scrutin.description",
                    "created_at": "$scrutin.created_at",
                    "is_active": "$scrutin.is_active",
                    "start_date": "$scrutin.start_date",
                    "end_date": "$scrutin.end_date",
                    "options": "$scrutin.options",
                    "votes": "$scrutin.votes",
                    "voter_preferences": "$scrutin.votes.preferences",
                    "creator_pseudonym": "$pseudonym" 
                }}
            ])
        )
        return scrutins
    
    @staticmethod
    def createScrutin(title, description, start_date, end_date, options, user_id):
        """ Créer un scrutin dans la base de données."""
        
        if isinstance(start_date, str) and len(start_date) == 10:  # Format date sans heure
            start_date += 'T00:00'

        if isinstance(end_date, str) and len(end_date) == 10:  # Format date sans heure
            end_date += 'T00:00'

        # Convertir les dates en objets datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M") if isinstance(start_date, str) else start_date
        end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M") if isinstance(end_date, str) else end_date


        # Créer un document de scrutin
        new_scrutin = {
            "scrutin_id": ObjectId(),
            "created_at": datetime.now(),
            "is_active": True,
            "title": title,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "options": options,
            "votes": []
        }

        # Insérer le scrutin dans la collection 'scrutins' de MongoDB
        current_app.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"scrutin": new_scrutin}}
        )
        return new_scrutin
    
    @staticmethod
    def find_by_user_and_id(user_id, scrutin_id):
        """Récupère le scrutin qui correspond à l'id du user et à l'id du scrutin"""
        scrutin_cursor = current_app.db.users.aggregate([
            {"$match":{"_id": ObjectId(user_id)}},
            {"$unwind": "$scrutin"},
            {"$match": {"scrutin.scrutin_id": ObjectId(scrutin_id)}},
            {"$project": {  # Sélectionner les champs nécessaires
                    "_id": 0,
                    "scrutin_id": "$scrutin.scrutin_id",
                    "title": "$scrutin.title",
                    "description": "$scrutin.description",
                    "created_at": "$scrutin.created_at",
                    "start_date": "$scrutin.start_date",
                    "end_date": "$scrutin.end_date",
                    "options": "$scrutin.options",
                    "voter_preferences": "$scrutin.votes.preferences",
                    "creator_pseudonym": "$pseudonym" 
                }}
        ])
        # Essayer d'obtenir le premier résultat du curseur
        scrutin = next(scrutin_cursor, None)
    
    # Si aucun résultat n'est trouvé
        if scrutin is None:
            return None
        return scrutin
    
    @staticmethod
    def updateScrutin(title, description, start_date, end_date, options, user_id, scrutin_id):
        """ Modifie un scrutin dans la base de données d'après son id."""

        # Si les dates sont au format "YYYY-MM-DD" (sans heure), ajouter l'heure à minuit
        if isinstance(start_date, str) and len(start_date) == 10:  
            start_date += 'T00:00'

        if isinstance(end_date, str) and len(end_date) == 10:  
            end_date += 'T00:00'

        # Convertir les dates en objets datetime si elles sont au format chaîne
        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M") if isinstance(start_date, str) else start_date
        end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M") if isinstance(end_date, str) else end_date

        # Vérification de la présence du scrutin_id
        if not scrutin_id:
            raise ValueError("Le scrutin_id est nécessaire pour mettre à jour un scrutin.")

        # Mettre à jour le scrutin dans le tableau "scrutin" de l'utilisateur
        result = current_app.db.users.update_one(
            {"_id": ObjectId(user_id), "scrutin.scrutin_id": ObjectId(scrutin_id)},  # Chercher l'utilisateur et le scrutin à mettre à jour
            {"$set": {
                "scrutin.$.title": title,
                "scrutin.$.description": description,
                "scrutin.$.start_date": start_date,
                "scrutin.$.end_date": end_date,
                "scrutin.$.options": options
            }}
        )

        # Afficher les informations de résultat pour le débogage
        print(f"matched_count: {result.matched_count}")
        print(f"modified_count: {result.modified_count}")
        
        # Si un scrutin a été mis à jour (c'est-à-dire que matched_count est supérieur à 0)
        if result.matched_count > 0:
            if result.modified_count > 0:
                return True  # Le scrutin a été mis à jour avec succès
            else:
                return False  # Aucun changement n'a été effectué, mais le scrutin a été trouvé
        else:
            return False  # Aucun scrutin trouvé pour la mise à jour
    
    @staticmethod
    def find_by_id(scrutin_id):
        """Récupère le scrutin qui correspond à l'id du user et à l'id du scrutin"""
        scrutin_cursor = current_app.db.users.aggregate([
            {"$unwind": "$scrutin"},
            {"$match": {"scrutin.scrutin_id": ObjectId(scrutin_id)}},
            {"$project": {  # Sélectionner les champs nécessaires
                    "_id": 0,
                    "scrutin_id": "$scrutin.scrutin_id",
                    "title": "$scrutin.title",
                    "description": "$scrutin.description",
                    "created_at": "$scrutin.created_at",
                    "is_active": "$scrutin.is_active",
                    "start_date": "$scrutin.start_date",
                    "end_date": "$scrutin.end_date",
                    "options": "$scrutin.options",
                    "voter_preferences": "$scrutin.votes.preferences",
                    "creator_pseudonym": "$pseudonym" 
                }}
        ])
        # Essayer d'obtenir le premier résultat du curseur
        scrutin = next(scrutin_cursor, None)
    
         # Si aucun résultat n'est trouvé
        if scrutin is None:
            return None
        return scrutin


    @staticmethod
    def find_user_vote(user_id, scrutin_id):
        """
        Vérifier si un utilisateur a voté pour un scrutin et récupérer ses préférences."""
        
        # Pipeline d'agrégation MongoDB
        result = current_app.db.users.aggregate([
            {"$unwind": "$scrutin"},  # Décomposer chaque scrutin
            {"$match": {"scrutin.scrutin_id": ObjectId(scrutin_id)}},  # Filtrer par scrutin_id
            {"$unwind": "$scrutin.votes"},  # Décomposer les votes
            {"$match": {"scrutin.votes.voter_id": ObjectId(user_id)}},  # Filtrer par voter_id
            {"$project": {  # Sélectionner uniquement les informations nécessaires
                "_id": 0,
                "created_at": "$scrutin.votes.created_at",
                "preferences": "$scrutin.votes.preferences",
                "creator_pseudonym": "$pseudonym" 

            }}
        ])
        
        # Extraire le premier résultat s'il existe
        vote = next(result, None)
        return vote if vote else None





    @staticmethod
    def addVote(votes, user_id, scrutin_id):
        """ Ajoute un vote à un scrutin d'après son Id."""
        new_vote = {
            "created_at": datetime.now(),
            "voter_id": ObjectId(user_id),
            "preferences": votes
        }

        result = current_app.db.users.update_one(
            {"scrutin.scrutin_id": ObjectId(scrutin_id)},  # Chercher le scrutin à mettre à jour
            {"$push": {
                "scrutin.$.votes": new_vote
            }}
        )
    

    @staticmethod
    def updateVote(new_preferences, user_id, scrutin_id):
        """Met à jour le vote d'un utilisateur pour un scrutin spécifique."""
        result = current_app.db.users.update_one(
            {
                "scrutin.scrutin_id": ObjectId(scrutin_id),  # Cherche le scrutin
                "scrutin.votes.voter_id": ObjectId(user_id)  # Vérifie que l'utilisateur a déjà voté
            },
            {
                "$set": {
                    "scrutin.$.votes.$.preferences": new_preferences,
                    "scrutin.$.votes.$.created_at": datetime.now()  # Met à jour la date du vote
                }
            }
        )