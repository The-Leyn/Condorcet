# apelle la function create_app qui se trouve dans /app (point d'entré __init__.py)
from app import create_app
import os
# stock la function sous app
app = create_app()
app.secret_key = os.urandom(24)
if __name__ == "__main__":
    # lance app
    app.run(debug=True)
