# Application de gestion de scrutins 🗳️

## Fonctionnalités ❌

### Front-End
#### 1. Pages publiques :
- Page d'accueil affichant la liste des 10 derniers scrutins créés et actifs : ❌ Page : index.html
- Page de création et de gestion des scrutins : ❌ Page : create-scrutin.html
- Page de résultats pour visualiser les consultations fermées : ❌ Page : results.html

#### 2. Interactions utilisateur :
- Inscription des utilisateurs avec pseudonyme unique : ❌ Page : signup.html
- Modification des informations personnelles, sauf pseudonyme : ❌ Page : profile.html
- Suppression partielle du profil (sauf pseudo et afficher comme "fermé")utilisateur tout en conservant l'historique des votes : ❌ Page : profile.html

#### 3. Participation aux scrutins :
- Interface de vote permettant de donner un ordre aux choix : ❌ Page : vote.html
- Modification des votes pour un scrutin ouvert : ❌ Page : edit-vote.html
- Visualisation des résultats sous forme de classement : ❌ Page : results.html

#### 4. Administration :
- Liste et modération des scrutins non conformes : ❌ Page : admin.html
- Statistiques d'utilisation de la plateforme : ❌ Page : stats.html

---

### Back-End
#### 1. Gestion des utilisateurs :
- Ajout d'un utilisateur avec pseudonyme et données personnelles : ❌ API : add-user.py
- Modification des données personnelles utilisateur : ❌ API : update-user.py
- Marquage d'un utilisateur comme "fermé" après désinscription : ❌ API : close-user.py

#### 2. Gestion des scrutins :
- Création d'un scrutin avec options configurables : ❌ API : add-scrutin.py
- Modification du texte d'un scrutin non public : ❌ API : edit-scrutin.py
- Fermeture automatique d'un scrutin à sa date de fin : ❌ API : close-scrutin.py
- Calcul des résultats par différents algorithmes : ❌ API : calculate-results.py

#### 3. Gestion des votes :
- Enregistrement des préférences d'un utilisateur pour un scrutin : ❌ API : add-vote.py
- Modification d'un vote existant pour un scrutin ouvert : ❌ API : update-vote.py
- Normalisation des votes pour le traitement algorithmique : ❌ API : normalize-vote.py

#### 4. Algorithmes de calcul :
- Algorithme de vote proportionnel (majorité simple) : ❌ Module : proportional-vote.py
- Algorithme de vote majoritaire (50%+1) : ❌ Module : majority-vote.py
- Algorithme de Condorcet pour classement des préférences : ❌ Module : condorcet-vote.py

---

### Base de données
#### 1. Structures de la base de données :
- Modèle pour les utilisateurs, scrutins et votes : ❌ Modèle : db-models.py

#### 2. Requêtes avancées :
- Liste des scrutins organisés par un utilisateur : ❌ API : user-scrutins.py
- Répartition des votes par année de naissance : ❌ API : vote-stats.py
- Nombre moyen d'options par scrutin : ❌ API : average-options.py
