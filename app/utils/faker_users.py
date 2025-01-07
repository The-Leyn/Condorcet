from faker import Faker
from pymongo import MongoClient
import random
from datetime import datetime, timedelta
from bson import ObjectId  # Importer ObjectId pour générer des ObjectId uniques
from werkzeug.security import generate_password_hash

# Initialiser Faker
fake = Faker()

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['condorcet']
users_collection = db['users']

# Générer un utilisateur administrateur unique
admin_user = {
    "_id": ObjectId(),
    "pseudonym": "admin",
    "firstname": "Admin",
    "lastname": "User",
    "email": "admin@email.com",
    "password_hash": generate_password_hash("adminPassword"),  # Mot de passe sécurisé
    "is_active": True,
    "role": "admin",
    "scrutin": []
}

# Insérer l'administrateur dans la collection
if not users_collection.find_one({"role": "admin"}):
    users_collection.insert_one(admin_user)
    print("👑 Utilisateur administrateur créé avec succès.")
else:
    print("⚠️ Un administrateur existe déjà dans la base de données.")

# Générer un utilisateur spécifique
specific_user = {
    "_id": ObjectId(),
    "pseudonym": "theRealJhon",
    "firstname": "Jhon",
    "lastname": "Doe",
    "email": "jhondoe@email.com",
    "password_hash": generate_password_hash("userPassword"),  # Mot de passe sécurisé
    "is_active": True,
    "role": "user",
    "scrutin": []
}

# Insérer l'utilisateur spécifique dans la collection
users_collection.insert_one(specific_user)
print("👤 Utilisateur spécifique créé avec succès : theRealJhon.")

# Générer des utilisateurs standards
existing_user_ids = [admin_user["_id"], specific_user["_id"]]  # Inclure l'administrateur et l'utilisateur spécifique dans la liste des ID existants

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
        "password_hash": generate_password_hash(fake.password(length=12)),
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
    
    # Créer un ObjectId pour la question
    question_id = ObjectId()
    
    return {
        "scrutin_id": question_id,  # Utiliser l'ObjectId comme question_id
        "created_at": start_date - timedelta(days=random.randint(0, 4)),  # Création dans un intervalle avant la start_date
        "title": fake.sentence(nb_words=6),
        "description": fake.text(max_nb_chars=100),
        "start_date": start_date,
        "end_date": end_date,
        "options": options,
        "votes": [generate_vote(options) for _ in range(random.randint(0, 5))]
    }

def generate_vote(options):
    voter_id = ObjectId(random.choice(existing_user_ids))
    return {
        "voter_id": voter_id,
        "preferences": random.sample(options, k=len(options))
    }

# Ajouter des scrutins pour l'administrateur et l'utilisateur spécifique
admin_scrutins = [generate_scrutin() for _ in range(random.randint(1, 3))]  # Scrutins de l'administrateur
specific_user_scrutins = [generate_scrutin() for _ in range(random.randint(1, 3))]  # Scrutins de l'utilisateur spécifique

# Mettre à jour l'administrateur et l'utilisateur spécifique dans la base de données
users_collection.update_one({"_id": admin_user['_id']}, {"$set": {"scrutin": admin_scrutins}})
users_collection.update_one({"_id": specific_user['_id']}, {"$set": {"scrutin": specific_user_scrutins}})

# Mettre à jour les autres utilisateurs avec des scrutins
for user in users_data:
    user['scrutin'] = [generate_scrutin() for _ in range(random.randint(1, 3))]
    users_collection.update_one({"_id": user['_id']}, {"$set": {"scrutin": user['scrutin']}})

print("✅ Données insérées et mises à jour avec succès dans la collection 'users'!")

# Fermer la connexion
client.close()
