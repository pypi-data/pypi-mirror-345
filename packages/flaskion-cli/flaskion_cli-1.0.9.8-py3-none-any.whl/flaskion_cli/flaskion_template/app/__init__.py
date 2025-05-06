from flask import Flask
from app.routes import register_routes
from flask_migrate import Migrate
from app.models import db


def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register all routes
    register_routes(app)

    return app