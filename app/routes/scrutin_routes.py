from flask import Blueprint, render_template, jsonify
from app.models.scrutin import ScrutinModel

# Définir le blueprint
scrutin_routes = Blueprint('scrutins', __name__)

@scrutin_routes.route('/scrutins', methods=['GET'])
def display_scrutins():
    """Afficher tous les scrutins."""
    scrutins = ScrutinModel.find_scrutins()
    return render_template('scrutins.html', scrutins=scrutins)

@scrutin_routes.route('/scrutins/<user_id>', methods=['GET'])
def display_user_scrutins(user_id):
    """Afficher les scrutins d'un utilisateur spécifique."""
    scrutins = ScrutinModel.find_scrutins_by_user(user_id)
    return render_template('scrutins.html', scrutins=scrutins)
