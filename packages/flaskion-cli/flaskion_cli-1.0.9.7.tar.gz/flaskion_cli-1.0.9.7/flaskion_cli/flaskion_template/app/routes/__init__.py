from flask import Flask
from app.routes.api_routes import api_routes
from app.routes.web_routes import web_routes

def register_routes(app: Flask):
    app.register_blueprint(api_routes)
    app.register_blueprint(web_routes)