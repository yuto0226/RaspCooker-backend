from sys import exit
from app import create_app
from app.config import configs

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
