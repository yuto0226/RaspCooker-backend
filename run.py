from sys import exit
from app import create_app
from app.config import configs

try:
    app = create_app()

except:
    exit()

if __name__ == "__main__":
    app.run()
