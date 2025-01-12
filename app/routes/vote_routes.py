from flask import Blueprint, jsonify, render_template, request

# Définir le blueprint
vote_routes = Blueprint('scrutin', __name__)

@vote_routes.route('/scrutin', methods=['GET', 'POST'])
def scrutin():
    from flask import request, render_template

    if request.method == 'GET':
        # Affiche le formulaire
        return render_template('scrutin-form.html')
    
@vote_routes.route('/scrutins', methods=['GET', 'POST'])
def scrutins():
    from flask import request, render_template

    if request.method == 'GET':
        # Affiche le formulaire
        return render_template('scrutins.html')

