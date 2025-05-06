from flask import Blueprint
from app.controllers.hello_controller import HelloController

web_routes = Blueprint("web_routes", __name__)

# Example Web Route
web_routes.add_url_rule("/", view_func=HelloController.index, methods=["GET"], endpoint="index_index")