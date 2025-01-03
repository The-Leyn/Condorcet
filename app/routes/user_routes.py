# app/routes/user_routes.py
from flask import Blueprint, jsonify, render_template, request, jsonify, redirect, url_for, session
from app.models.user import UserModel
import logging

# Définir le blueprint
user_routes = Blueprint('user', __name__)

@user_routes.route('/users', methods=['GET'])
def get_users():
    """Récupérer les informations d'un utilisateur."""
    users = UserModel.find_all_user()
    if users:
        return render_template("index_user.html", users=users)
    return jsonify({"error": "User not found"}), 404

@user_routes.route('/user/<id_user>', methods=['GET'])
def get_user(id_user):
    """Récupérer les informations d'un utilisateur."""
    user = UserModel.find_by_id_user(id_user)
    if user:
        return render_template("profile.html", user=user)
    return jsonify({"error": "User not found"}), 404


# Connexion by Christopher
@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Vérification des champs vides
        if not email or not password:
            error_message = "Veuillez remplir tous les champs."
            return render_template("login.html", error=error_message)

        # Vérification des informations d'identification
        response, success = UserModel.login(email, password)
        if success:
            return redirect(url_for('main.home'))
        else:
            return render_template("login.html", error=response["error"])

    # Afficher le formulaire pour la méthode GET
    return render_template("login.html")


@user_routes.route("/logout", methods=["GET"])
def logout():
    if 'user_id' not in session:
        return redirect(url_for('main.home'))
    else:
        UserModel.logout()
        return redirect(url_for('main.home'))