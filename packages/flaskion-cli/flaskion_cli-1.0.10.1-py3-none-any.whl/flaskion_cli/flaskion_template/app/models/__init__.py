from flask_sqlalchemy import SQLAlchemy
import os
import importlib

db = SQLAlchemy()

# Dynamically import all model modules in this directory
model_dir = os.path.dirname(__file__)
for filename in os.listdir(model_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"app.models.{filename[:-3]}"
        importlib.import_module(module_name)