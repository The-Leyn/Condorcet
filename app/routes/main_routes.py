from flask import Blueprint, jsonify, render_template, request
from app.models.scrutin import ScrutinModel
from datetime import datetime

# Création du blueprint
main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    scrutins = ScrutinModel.find_10_last()
    scrutinsActive = ScrutinModel.find_10_last_active()
    if scrutins and scrutinsActive:
        return render_template("home.html", scrutins=scrutins, scrutinsActive=scrutinsActive)
    return jsonify({"error": "Scrutins not found"}), 404
