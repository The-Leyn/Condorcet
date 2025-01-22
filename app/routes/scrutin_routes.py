# app/routes/scrutin_routes.py
from flask import flash, current_app, Blueprint, jsonify, render_template, request, jsonify, redirect, url_for, session
from app.models.user import UserModel
from app.models.scrutin import ScrutinModel
from bson.objectid import ObjectId
from datetime import datetime

scrutin_routes = Blueprint('scrutin', __name__)
@scrutin_routes.context_processor
def inject_now():
    return {'now': datetime.now}

@scrutin_routes.route('/scrutins/', methods=["GET"])
def index_scrutin():
    
    scrutins = ScrutinModel.find_all_scrutin()
    return render_template("scrutins.html", scrutins=scrutins, session=session)
 
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
                # Vérification si la end_date est supérieure à la start_date
        if end_date <= start_date:
            return render_template("scrutin_form/add_scrutin_form.html", error="La date de fin doit être supérieure à la date de début.")

        # Vérification si au moins 2 options sont fournies
        if len(options) < 2:
            return render_template("scrutin_form/add_scrutin_form.html", error="Il doit y avoir au moins 2 options.")
        # Vérification si des options sont en double
        if len(options) != len(set(options)):
            return render_template("scrutin_form/add_scrutin_form.html", error="Les options ne peuvent pas être en double.")

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
            return redirect(url_for('user.get_user_profile', action='scrutins'))  # À adapter selon ta logique de redirection

        except Exception as e:
            # Si une exception se produit, afficher l'erreur
            return render_template("scrutin_form/add_scrutin_form.html", error=f"Une erreur est survenue lors de la création du scrutin : {str(e)}")
        
    return render_template("scrutin_form/add_scrutin_form.html")

@scrutin_routes.route('/scrutins/edit/<string:scrutin_id>', methods=["GET", "POST"])
def edit_scrutin(scrutin_id):
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    user_id = session.get('user_id')
    getScrutin = ScrutinModel.find_by_user_and_id(user_id, scrutin_id)
    current_time = datetime.now()
    if getScrutin["start_date"] < current_time:
        return redirect(url_for('user.get_user_profile')) 
        
    if request.method == "POST":
        # Récupérer les données du formulaire
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        options = request.form.getlist('options[]')  # Récupérer toutes les options du formulaire

        # Vérification si tous les champs sont remplis
        if not title or not description or not start_date or not end_date:
            return redirect(url_for('user.edit_scrutin', scrutin_id=scrutin_id))
        # Vérification si la end_date est supérieure à la start_date
        if end_date <= start_date:
            return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=getScrutin, error="La date de fin doit être supérieure à la date de début.")
        # Vérification si au moins 2 options sont fournies
        if len(options) < 2:
            return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=getScrutin, error="Il doit y avoir au moins 2 options.")
        # Vérification si des options sont en double
        if len(options) != len(set(options)):
            return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=getScrutin, error="Les options ne peuvent pas être en double.")

        if any(option.strip() == "" for option in options):  # On vérifie si une option est vide
            return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=getScrutin, error="Aucune option ne peut être vide.")
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
            flash("L'opération s'est bien déroulée.", "success")
            return redirect(url_for('scrutin.edit_scrutin', scrutin_id=scrutin_id))

        except Exception as e:
            # Si une exception se produit, afficher l'erreur
            return render_template("scrutin_form/edit_scrutin_form.html", error=f"Une erreur est survenue lors de la création du scrutin : {str(e)}")
    
    scrutin_id = ObjectId(scrutin_id)
    scrutin = ScrutinModel.find_by_user_and_id(user_id,scrutin_id)
    if not scrutin:
        # Si aucun scrutin trouvé, rediriger 
        return redirect(url_for('scrutin.index_scrutin'))  
    
    return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=scrutin)


@scrutin_routes.route('/scrutins/<string:scrutin_id>', methods=["GET", "POST"])
def add_vote(scrutin_id):
    """Page de vote d'un scrutin"""
    
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session.get('user_id')
    current_time = datetime.now()
    scrutin = ScrutinModel.find_by_id(scrutin_id)

    if not scrutin:
        return redirect(url_for('scrutin.index_scrutin'))  # Rediriger si le scrutin n'existe pas

    # Vérifier si le scrutin est terminé
    if scrutin['end_date'] < current_time:
        return redirect(url_for('scrutin.result', scrutin_id=scrutin_id)) 

    if request.method == "POST":
        # Récupérer les préférences du formulaire
        preferences = request.form.getlist('preferences[]')
        print("Données de 'preferences[]' :", preferences)

        # Récupérer les options valides pour ce scrutin
        options = ScrutinModel.get_scrutin_options(scrutin_id)  # Méthode à implémenter dans ton modèle
        print("Options valides pour le scrutin :", options)

        # Vérifier que toutes les préférences sont valides
        if not set(preferences).issubset(set(options)):
            print("Erreur : Les préférences contiennent des valeurs non valides.")
            return render_template(
                "scrutin_form/vote_scrutin_form.html", 
                scrutin_id=scrutin_id, 
                scrutin=scrutin, 
                error="Certaines des préférences soumises ne sont pas valides.",
                current_time=current_time, 
            )

        # Vérifier si l'utilisateur a déjà voté
        vote_info = ScrutinModel.find_user_vote(user_id, scrutin_id)
        if vote_info:
            ScrutinModel.updateVote(preferences, user_id, scrutin_id)
            
            return redirect(url_for('scrutin.add_vote', scrutin_id=scrutin_id)) 
        else:
            ScrutinModel.addVote(preferences, user_id, scrutin_id)
            return redirect(url_for('scrutin.add_vote', scrutin_id=scrutin_id))
        
    # Verifier si le scrutin est terminé
    if scrutin['end_date'] < current_time:
        return render_template("results.html", scrutin_id=scrutin_id)
    
    # Vérifier si l'utilisateur a déjà voté
    vote_info = ScrutinModel.find_user_vote(user_id, scrutin_id)
    if vote_info:
        print(f"L'utilisateur a voté avec les informations suivantes : {vote_info}")
        return render_template(
            "scrutin_form/vote_scrutin_form.html", 
            current_time=current_time, 
            scrutin_id=scrutin_id, 
            vote_info=vote_info, 
            scrutin=scrutin
        )
    else:
        print("L'utilisateur n'a pas voté pour ce scrutin.")
        return render_template(
            "scrutin_form/vote_scrutin_form.html", 
            current_time=current_time, 
            scrutin_id=scrutin_id, 
            scrutin=scrutin
        )


@scrutin_routes.route('/scrutins/result/<string:scrutin_id>', methods=["GET", "POST"])
def result(scrutin_id):
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    user_id = session.get('user_id')
    current_time = datetime.now()

    scrutin = ScrutinModel.find_by_id(scrutin_id)

    #Vérifier si le scrutin est terminé
    if scrutin['end_date'] > current_time:
        print("Le scrutin n'est pas encore terminé")
        return redirect(url_for('scrutin.add_vote', scrutin_id=scrutin_id))
    

    if request.method == "POST":

        isScrutin = ScrutinModel.find_by_user_and_id(user_id, scrutin_id)
        # Si c'est le user est le créateur du scrutin alors calculé   
        if isScrutin:
            ScrutinModel.calculate_condorcet_and_save(scrutin_id, user_id)


    # Vérifier si les résultats on été calculé
    result = ScrutinModel.get_scrutin_result(scrutin_id)
    if result:
        # Si oui les afficher

        return render_template("results.html", scrutin_id=scrutin_id, result=result, session_user_id=user_id)
    else:
        return render_template("results.html", scrutin_id=scrutin_id, scrutin=scrutin, session_user_id=user_id)
    
@scrutin_routes.route('/deactivate_scrutin', methods=['POST'])
def deactivate_scrutin():
    """Désactive le compte de l'utilisateur connecté."""
    if 'user_id' not in session:
        return redirect(url_for('main.home'))
    
    user_id = session['user_id']  # Récupérer l'utilisateur connecté

    if request.method == "POST":
        scrutin_id = request.form.get('scrutin_id')

        if scrutin_id:
            success = ScrutinModel.disableScrutinAsAdmin(scrutin_id, user_id)
            return redirect(url_for('scrutin.index_scrutin'))
        else:
            return redirect(url_for('scrutin.index_scrutin'))