from flask import Flask
from pymongo import MongoClient

def create_app():
    # Crée une instance de l'application Flask
    app = Flask(__name__)

    # Configuration MongoDB
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/condorcet'

    # Connexion à MongoDB
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.condorcet  # Ajout de la base de données à l'application

    # Importer les blueprints
    from .routes import main_routes, user_routes

    # Enregistrer les blueprints
    app.register_blueprint(main_routes)
    app.register_blueprint(user_routes)

    return app
