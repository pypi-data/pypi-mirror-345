from mlflow.server import app
from flask import Flask
from flask_cors import CORS

def create_app(app: Flask = app):
    CORS(app)
    return app