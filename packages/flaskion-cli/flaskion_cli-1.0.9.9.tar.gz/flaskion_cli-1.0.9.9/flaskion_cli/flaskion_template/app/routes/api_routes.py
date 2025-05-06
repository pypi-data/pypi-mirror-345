from flask import Blueprint, jsonify
from app.controllers.api_controller import APIController

api_routes = Blueprint("api_routes", __name__, url_prefix="/api")

# Define a route for the API Hello World
api_routes.add_url_rule("/hello", view_func=APIController.hello, methods=["GET"], endpoint="index_hello")