from faker import Faker
from pymongo import MongoClient
import random
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Initialiser Faker
fake = Faker()

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['condorcet']
users_collection = db['users']

# Générer des données faker pour la collection users
existing_user_ids = []

# Pré-générer les utilisateurs pour garantir qu'ils existent avant les votes
users_data = []
for _ in range(100):
    user_id = ObjectId()
    existing_user_ids.append(user_id)
    users_data.append({
        "_id": user_id,
        "pseudonym": fake.user_name(),
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "email": fake.email(),
        "password_hash": fake.password(length=12),
        "is_active": random.choice([True, False]),
        "role": "user",
        "scrutin": []
    })

# Insérer les utilisateurs dans MongoDB
users_collection.insert_many(users_data)

# Ajouter les scrutins après que les utilisateurs existent déjà
def generate_scrutin():
    start_date = fake.date_time_between(start_date='-90d', end_date='now')
    end_date = start_date + timedelta(days=random.randint(1, 90))
    options = [fake.word() for _ in range(random.randint(2, 5))]
    return {
        "question_id": f"question{random.randint(100, 999)}",
        "title": fake.sentence(nb_words=6),
        "description": fake.text(max_nb_chars=100),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "options": options,
        "votes": [generate_vote(options) for _ in range(random.randint(0, 5))]
    }

def generate_vote(options):
    voter_id = str(random.choice(existing_user_ids))
    return {
        "voter_id": voter_id,
        "preferences": random.sample(options, k=len(options))
    }

# Mettre à jour les utilisateurs avec des scrutins
for user in users_data:
    user['scrutin'] = [generate_scrutin() for _ in range(random.randint(1, 3))]
    users_collection.update_one({"_id": user['_id']}, {"$set": {"scrutin": user['scrutin']}})

print("Données insérées et mises à jour avec succès dans la collection 'users'!")

# Fermer la connexion
client.close()
