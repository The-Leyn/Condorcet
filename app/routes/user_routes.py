# app/routes/user_routes.py
from flask import Blueprint, jsonify, render_template, request, jsonify, redirect, url_for, session
from app.models.user import UserModel
from werkzeug.security import generate_password_hash
from app.models.scrutin import ScrutinModel
from datetime import datetime
import re

# Définir le blueprint
user_routes = Blueprint('user', __name__)
@user_routes.context_processor
def inject_now():
    return {'now': datetime.now}

@user_routes.route('/users', methods=['GET'])
def get_users():
    """Récupérer les informations d'un utilisateur."""
    users = UserModel.find_all_user()
    if users:
        return render_template("index_user.html", users=users)
    return jsonify({"error": "User not found"}), 404

# PROFILE
@user_routes.route('/profile/<action>', methods=['GET'])
def get_user_profile(action):
    """Afficher le profil d'un utilisateur"""
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    current_time = datetime.now()
    user_id = session.get('user_id')
    user = UserModel.find_by_id_user(user_id)
    
    scrutins = None
    if action == 'scrutins':
        scrutins = ScrutinModel.find_created_by_user(user_id)
    elif action == 'participate':
        scrutins = ScrutinModel.find_user_participations(user_id)
    else:
        return jsonify({"error": "Invalid action"}), 400
    
    if user:
        return render_template("profile.html", current_time=current_time, user=user, scrutins=scrutins, action=action)
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
    
@user_routes.route("/register", methods=["GET", "POST"])
def register():
    
    if 'user_id' in session:
        return redirect(url_for('main.home'))
    
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":

        email = request.form.get('email')
        pseudonym = request.form.get('pseudonym')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        repeatpassword = request.form.get('repeatpassword')

        if not email or not password or not pseudonym or not firstname or not lastname:
            error_message = "Veuillez remplir tous les champs."
            return render_template("register.html", error=error_message)

        if password != repeatpassword:
            error_message = "Les mots de passe ne correspondent pas."
            return render_template("register.html", error=error_message)
        
        # Vérification du format de l'email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_message = "Adresse e-mail invalide."
            return render_template("register.html", error=error_message)

        if UserModel.find_by_email(email):
            error_message = "L'email est déjà utilisé."
            return render_template("register.html", error=error_message)
        # création de l'utilisateur
        try:
            user_data = {
                "pseudonym": pseudonym,
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "password_hash": password,
                "is_active": True,
                "role": "user",
                "scrutin": [],
            }
            UserModel.register(user_data)
            return redirect(url_for('main.home'))
        except ValueError as e:
            error_message = str(e)
            return render_template("register.html", error=error_message)
            
@user_routes.route('/deactivate_account', methods=['POST'])
def deactivate_account():
    """Désactive le compte de l'utilisateur connecté."""
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session['user_id']  # Récupérer l'utilisateur connecté
    success = UserModel.deactivate_user(user_id)
    
    if success:
        # Déconnecter l'utilisateur après désactivation
        session.clear()
        return redirect(url_for('user.login'))
    else:
        return redirect(url_for('user.profile'))
    


@user_routes.route("/edit-profile", methods=["GET", "POST"])
def edit_user():
    def is_valid_email(email):
        """Valide l'adresse e-mail."""
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.match(email_regex, email) is not None
    
    """Modifier le profil de l'utilisateur."""
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session.get('user_id')
    user = UserModel.find_by_id_user(user_id)
    
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    if request.method == "GET":
        # Affiche le formulaire avec les données actuelles
        return render_template("edit_user.html", user=user)

    if request.method == "POST":
        # Récupérer les nouvelles données
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")

        # Validation des champs requis
        if not firstname or not lastname or not email:
            error_message = "Veuillez remplir tous les champs."
            print(error_message, "error")
            return jsonify({"error": error_message}), 400  # Retourne un code 400 pour les champs manquants

        # Validation de l'email
        if not is_valid_email(email):
            error_message = "Adresse e-mail invalide"
            print(error_message, "error")
            return render_template("edit_user.html", user=user, error=error_message)

        try:
            # Mise à jour des données dans la base
            updated_data = {
                "firstname": firstname,
                "lastname": lastname,
                "email": email
            }
            UserModel.update_user(user_id, updated_data)
            
            # Message de succès et redirection
            print("Profil mis à jour avec succès.", "success")
            return redirect(url_for('user.get_user_profile'))
        except Exception as e:
            print(f"Une erreur est survenue : {str(e)}", "error")
            return redirect(url_for('user.edit_user'))
