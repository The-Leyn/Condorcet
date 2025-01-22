from flask import flash, current_app, Blueprint, jsonify, render_template, request, jsonify, redirect, url_for, session
from app.models.scrutin import ScrutinModel
from app.models.user import UserModel
from datetime import datetime

admin_routes = Blueprint('admin', __name__)
@admin_routes.context_processor
def inject_now():
    return {'now': datetime.now}

@admin_routes.route('/dashboard/', methods=["GET"])
def dashboard():
    """ Récupérer tous les scrutins, calculer la moyenne des options par scrutin, et afficher les données dans le template. """
    
    # Récupérer tous les scrutins
    scrutins = ScrutinModel.find_all_scrutin()
    
    # # Récupérer les 10 scrutins les plus populaires
    top_scrutins = ScrutinModel.find_top_10_scrutins_by_participants()
    
    # Calculer le nombre total d'options et le nombre de scrutins
    total_options = sum(len(scrutin['options']) for scrutin in scrutins)
    total_scrutins = len(scrutins)

    # Calculer la moyenne des options pour tous les scrutins (arrondie à 2 chiffres)
    if total_scrutins > 0:
        average_options = round(total_options / total_scrutins, 2)
    else:
        average_options = 0.0

    """Récupérer les informations d'un utilisateur."""
    users = UserModel.find_all_user()
    user_count = UserModel.count_users()  # Nombre total d'utilisateurs
    active_user_count = UserModel.count_active_users()  # Nombre d'utilisateurs actifs

    # Passer les scrutins et la moyenne des options au template
    return render_template("dashboard.html", total_scrutins=total_scrutins, scrutins=scrutins, average_options=average_options, users=users, user_count=user_count, active_user_count=active_user_count, top_scrutins=top_scrutins)

