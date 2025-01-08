# app/routes/scrutin_routes.py
from flask import flash, current_app, Blueprint, jsonify, render_template, request, jsonify, redirect, url_for, session
from app.models.user import UserModel
from app.models.scrutin import ScrutinModel
from bson.objectid import ObjectId

# Définir le blueprint
scrutin_routes = Blueprint('scrutin', __name__)
@scrutin_routes.route('/scrutins', methods=["GET"])
def index_scrutin():
    # Récupérer tous les scrutins
    scrutins = ScrutinModel.find_all_scrutin()
    # Passer les scrutins au template
    return render_template("scrutins.html" , scrutins=scrutins)

@scrutin_routes.route('/scrutins/add', methods=["GET", "POST"])
def create_scrutin():
    """Créer un scrutin"""
    
    if 'user_id' not in session:
        return redirect(url_for('user.login')) 
    
    if request.method == "POST":
        # Récupérer les données du formulaire
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        options = request.form.getlist('options[]')  # Récupérer toutes les options du formulaire

        # Vérification si tous les champs sont remplis
        if not title or not description or not start_date or not end_date:
            return render_template("scrutin_form/add_scrutin_form.html", error="Tous les champs doivent être remplis.")
        
        # Vérification si au moins 2 options sont fournies
        if len(options) < 2:
            return render_template("scrutin_form/add_scrutin_form.html", error="Il doit y avoir au moins 2 options.")
        
        if any(option.strip() == "" for option in options):  # On vérifie si une option est vide
            return render_template("scrutin_form/add_scrutin_form.html", error="Aucune option ne peut être vide.")
        try:
            # Appeler la méthode createScrutin() pour créer le scrutin
            scrutin = ScrutinModel.createScrutin(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                options=options,
                user_id=session['user_id']  # L'ID de l'utilisateur venant de la session
            )

            # Rediriger vers une page de succès ou d'affichage du scrutin
            return redirect(url_for('user.get_user_profile'))  # À adapter selon ta logique de redirection

        except Exception as e:
            # Si une exception se produit, afficher l'erreur
            return render_template("scrutin_form/add_scrutin_form.html", error=f"Une erreur est survenue lors de la création du scrutin : {str(e)}")
        
    return render_template("scrutin_form/add_scrutin_form.html")


@scrutin_routes.route('/scrutins/edit/<string:scrutin_id>', methods=["GET", "POST"])
def edit_scrutin(scrutin_id):
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    if request.method == "POST":
        # Récupérer les données du formulaire
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        options = request.form.getlist('options[]')  # Récupérer toutes les options du formulaire

        # Vérification si tous les champs sont remplis
        if not title or not description or not start_date or not end_date:
            return render_template("scrutin_form/add_scrutin_form.html", error="Tous les champs doivent être remplis.")
        
        # Vérification si au moins 2 options sont fournies
        if len(options) < 2:
            return render_template("scrutin_form/add_scrutin_form.html", error="Il doit y avoir au moins 2 options.")
        
        if any(option.strip() == "" for option in options):  # On vérifie si une option est vide
            return render_template("scrutin_form/add_scrutin_form.html", error="Aucune option ne peut être vide.")
        try:
            scrutin = ScrutinModel.updateScrutin(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                options=options,
                user_id=session['user_id'],# L'ID de l'utilisateur venant de la session
                scrutin_id=scrutin_id
            )
            if not scrutin:
                return render_template("scrutin_form/edit_scrutin_form.html", error="Le scrutin n'a pas pu être mis à jour.")
            # Rediriger vers une page de succès ou d'affichage du scrutin
            return redirect(url_for('scrutin.edit_scrutin', scrutin_id=scrutin_id))  # À adapter selon ta logique de redirection

        except Exception as e:
            # Si une exception se produit, afficher l'erreur
            return render_template("scrutin_form/edit_scrutin_form.html", error=f"Une erreur est survenue lors de la création du scrutin : {str(e)}")
    
    user_id = session.get('user_id')
    scrutin_id = ObjectId(scrutin_id)
    scrutin = ScrutinModel.find_by_user_and_id(user_id,scrutin_id)
    if not scrutin:
        # Si aucun scrutin trouvé, rediriger ou afficher un message d'erreur
        # flash("Ce scrutin n'existe pas ou vous n'avez pas les droits pour le modifier.", "error")
        return redirect(url_for('scrutin.index_scrutin'))  # Rediriger vers la page d'index des scrutins
    
    return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=scrutin)