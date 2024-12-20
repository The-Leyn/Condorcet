# apelle la function create_app qui se trouve dans /app (point d'entré __init__.py)
from app import create_app

# stock la function sous app
app = create_app()

if __name__ == "__main__":
    # lance app
    app.run(debug=True)
