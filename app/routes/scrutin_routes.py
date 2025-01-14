# app/routes/scrutin_routes.py
from flask import flash, current_app, Blueprint, jsonify, render_template, request, jsonify, redirect, url_for, session
from app.models.user import UserModel
from app.models.scrutin import ScrutinModel
from bson.objectid import ObjectId
from datetime import datetime

scrutin_routes = Blueprint('scrutin', __name__)
@scrutin_routes.route('/scrutins', methods=["GET"])
def index_scrutin():
    """ Récupérer tous les scrutins, calculer la moyenne des options par scrutin, et afficher les données dans le template. """
    # Récupérer tous les scrutins
    scrutins = ScrutinModel.find_all_scrutin()

    # Calculer le nombre total d'options et le nombre de scrutins
    total_options = sum(len(scrutin['options']) for scrutin in scrutins)
    total_scrutins = len(scrutins)

    # Calculer la moyenne des options pour tous les scrutins (arrondie à 2 chiffres)
    if total_scrutins > 0:
        average_options = round(total_options / total_scrutins, 2)
    else:
        average_options = 0.0

    # Passer les scrutins et la moyenne des options au template
    return render_template("scrutins.html", scrutins=scrutins, average_options=average_options)

@scrutin_routes.route('/scrutins', methods=['GET'])
def afficher_scrutins_10_populaire():
    """
    Afficher tous les scrutins et les 10 scrutins les plus participés.
    """
    try:
        # Récupérer tous les scrutins
        scrutins = list(current_app.db.scrutins.find())

        # Récupérer les 10 scrutins avec le plus de participants
        top_scrutins = list(current_app.db.scrutins.aggregate([
            {"$addFields": {"vote_count": {"$size": {"$ifNull": ["$votes", []]}}}},  # Calculer le nombre de votes
            {"$sort": {"vote_count": -1}},  # Trier par le nombre de votes décroissant
            {"$limit": 10}  # Limiter à 10 résultats
        ]))

        # Calculer la moyenne des options pour tous les scrutins
        total_options = sum(len(scrutin.get("options", [])) for scrutin in scrutins)
        average_options = round(total_options / len(scrutins), 2) if scrutins else 0

        # Calculer la moyenne des votes pour les top scrutins
        total_votes = sum(scrutin.get("vote_count", 0) for scrutin in top_scrutins)
        average_votes = round(total_votes / len(top_scrutins), 2) if top_scrutins else 0

        return render_template(
            'scrutin.html',
            scrutins=scrutins,
            average_options=average_options,
            top_scrutins=top_scrutins,
            average_votes=average_votes
        )
    except Exception as e:
        return {"error": f"Une erreur est survenue : {str(e)}"}, 500

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
            return redirect(url_for('user.get_user_profile'))  # À adapter selon ta logique de redirection

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
            return redirect(url_for('user.edit_scrutin', scrutin_id=scrutin_id))  # À adapter selon ta logique de redirection
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
            return redirect(url_for('scrutin.edit_scrutin', scrutin_id=scrutin_id))  # À adapter selon ta logique de redirection

        except Exception as e:
            # Si une exception se produit, afficher l'erreur
            return render_template("scrutin_form/edit_scrutin_form.html", error=f"Une erreur est survenue lors de la création du scrutin : {str(e)}")
    
    scrutin_id = ObjectId(scrutin_id)
    scrutin = ScrutinModel.find_by_user_and_id(user_id,scrutin_id)
    if not scrutin:
        # Si aucun scrutin trouvé, rediriger ou afficher un message d'erreur
        # flash("Ce scrutin n'existe pas ou vous n'avez pas les droits pour le modifier.", "error")
        return redirect(url_for('scrutin.index_scrutin'))  # Rediriger vers la page d'index des scrutins
    
    return render_template("scrutin_form/edit_scrutin_form.html", scrutin_id=scrutin_id, scrutin=scrutin)


@scrutin_routes.route('/scrutins/<string:scrutin_id>', methods=["GET", "POST"])
def add_vote(scrutin_id):
    """Page de vote d'un scrutin"""
    
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session.get('user_id')
    current_time = datetime.now()
    scrutin = ScrutinModel.find_by_id(scrutin_id)

    if request.method == "POST":
        # Récupérer toutes les données du formulaire
        print("Données brutes du formulaire :")
        print(request.form)  # Affiche tout ce que le formulaire envoie

        # Récupérer une clé spécifique (par exemple 'preferences[]')
        preferences = request.form.getlist('preferences[]')  # Utilisez getlist pour récupérer une liste
        print("Données de 'preferences[]' :")
        print(preferences)

        # Si l'utilisateur à déja voté
        vote_info = ScrutinModel.find_user_vote(user_id, scrutin_id)
        if vote_info:
            ScrutinModel.updateVote(preferences, user_id, scrutin_id)
            return redirect(url_for('scrutin.add_vote', scrutin_id=scrutin_id))  # À adapter selon ta logique de redirection

        #Si l'utilisateur n'as pas encore voté
        else:
            ScrutinModel.addVote(preferences, user_id, scrutin_id)
            return redirect(url_for('scrutin.add_vote', scrutin_id=scrutin_id))  # À adapter selon ta logique de redirection




    # # Verifier si le scrutin est en cours
    # if scrutin['start_date'] < current_time and scrutin['end_date'] > current_time:
    #     return render_template("scrutin_form/vote_scrutin_form.html", scrutin_id=scrutin_id)
    

    # Verifier si le scrutin est terminé
    if scrutin['end_date'] < current_time:
        return render_template("results.html", scrutin_id=scrutin_id)
    
    # Verifier si l'utilisateur à déjà voté
    vote_info = ScrutinModel.find_user_vote(user_id, scrutin_id)
    if vote_info:
        print(f"L'utilisateur a voté avec les informations suivantes : {vote_info}")
        return render_template("scrutin_form/vote_scrutin_form.html", current_time=current_time, scrutin_id=scrutin_id, vote_info=vote_info, scrutin=scrutin)
    else:
        print("L'utilisateur n'a pas voté pour ce scrutin.")
        return render_template("scrutin_form/vote_scrutin_form.html", current_time=current_time, scrutin_id=scrutin_id, scrutin=scrutin)
    

    # ScrutinModel.addVote(["day", "theory", "nature", "hot", "certainly"], "6782803d7efa1e356fabc503", "678280427efa1e356fabc56a")
    # if request.method == "POST":
    #     # Récupérer les données du formulaire
    #     title = request.form.get('title')
    #     description = request.form.get('description')
    #     start_date = request.form.get('start_date')
    #     end_date = request.form.get('end_date')
    #     options = request.form.getlist('options[]')  # Récupérer toutes les options du formulaire

    #     # Vérification si tous les champs sont remplis
    #     if not title or not description or not start_date or not end_date:
    #         return render_template("scrutin_form/add_scrutin_form.html", error="Tous les champs doivent être remplis.")
        
    #     # Vérification si au moins 2 options sont fournies
    #     if len(options) < 2:
    #         return render_template("scrutin_form/add_scrutin_form.html", error="Il doit y avoir au moins 2 options.")
        
    #     if any(option.strip() == "" for option in options):  # On vérifie si une option est vide
    #         return render_template("scrutin_form/add_scrutin_form.html", error="Aucune option ne peut être vide.")
    #     try:
    #         # Appeler la méthode createScrutin() pour créer le scrutin
    #         scrutin = ScrutinModel.createScrutin(
    #             title=title,
    #             description=description,
    #             start_date=start_date,
    #             end_date=end_date,
    #             options=options,
    #             user_id=session['user_id']  # L'ID de l'utilisateur venant de la session
    #         )

    #         # Rediriger vers une page de succès ou d'affichage du scrutin
    #         return redirect(url_for('user.get_user_profile'))  # À adapter selon ta logique de redirection

    #     except Exception as e:
    #         # Si une exception se produit, afficher l'erreur
    #         return render_template("scrutin_form/add_scrutin_form.html", error=f"Une erreur est survenue lors de la création du scrutin : {str(e)}")
        
    return render_template("scrutin_form/vote_scrutin_form.html", scrutin_id=scrutin_id)