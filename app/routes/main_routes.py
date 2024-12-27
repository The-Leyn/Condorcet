from flask import Blueprint
from flask import render_template

# Création du blueprint
main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return "Bienvenue sur la page d'accueil !"
