from flask import Blueprint, jsonify, render_template, request, session
from app.models.scrutin import ScrutinModel
from datetime import datetime

# Création du blueprint
main_routes = Blueprint('main', __name__)
@main_routes.context_processor
def inject_now():
    return {'now': datetime.now}
@main_routes.route('/')
def home():
    # session['user_email'] = "test@email.com"  # Optionnel, stocke aussi l'email
    
    scrutins = ScrutinModel.find_10_last()
    scrutinsActive = ScrutinModel.find_10_last_active()
    if scrutins and scrutinsActive:
        return render_template("home.html", scrutins=scrutins, scrutinsActive=scrutinsActive, session=session)
    return jsonify({"error": "Scrutins not found"}), 404
