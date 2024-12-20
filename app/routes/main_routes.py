from flask import Blueprint

# Création du blueprint
main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return "Bienvenue sur la page d'accueil !"
