# app/routes/user_routes.py
from flask import Blueprint, jsonify, render_template, request, jsonify
from werkzeug.security import generate_password_hash
from app.models.user import UserModel, loginForm
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
        # return jsonify(user), 200
        return render_template("profile.html", user=user)
    return jsonify({"error": "User not found"}), 404

@user_routes.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Afficher le formulaire ou ajouter un nouvel utilisateur."""
    from flask import request, render_template
    from app.models.user import UserModel

    if request.method == 'GET':
        # Affiche le formulaire
        return render_template('add_user.html')

    if request.method == 'POST':
        # Traite les données du formulaire
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validation simple
        if not username or not email or not password:
            return {"error": "Tous les champs sont obligatoires"}, 400
        
        password = generate_password_hash(password)

        # Insérer l'utilisateur dans la base de données
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password  # Exemple de hachage
        }
        UserModel.create_user(user_data)

        return {"message": "Utilisateur ajouté avec succès"}, 201


# Connexion by Christopher

@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Vérification des champs vides
        if not email or not password:
            error_message = "Veuillez remplir tous les champs."
            return render_template("login.html", error=error_message)

        # Vérification des informations d'identification
        response, success = loginForm.login(email, password)
        if success:
            return render_template("home.html")
        else:
            return render_template("login.html", error=response["error"])

    # Afficher le formulaire pour la méthode GET
    return render_template("login.html")

