import click
import os
import shutil
import subprocess
import importlib.resources
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def get_template_env():
    with importlib.resources.path("flaskion_cli", "cli_templates") as template_dir:
        return Environment(loader=FileSystemLoader(str(template_dir)))

@click.group()
def cli():
    pass

@cli.command(name="make:new")
@click.argument("project_name")
@click.option("--db", default="sqlite", type=click.Choice(["sqlite", "mysql", "postgres"]), help="Database to use")
def new(project_name, db):
    """
    Create a new Flaskion project.

    This will:
    • Copy the default Flaskion template into a new folder
    • Initialise a Git repository
    • Create a virtual environment
    • Install base dependencies via requirements.txt
    • Install DB-specific driver (MySQL/Postgres only)
    • Generate a .env file based on the DB type

    Example:
        flaskion make:new myapp --db=mysql
    """
    template_path = os.path.join(os.path.dirname(__file__), "flaskion_template")
    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        click.echo(f"❌ Project '{project_name}' already exists.")
        return

    # Step 1: Copy template
    shutil.copytree(template_path, project_path)
    click.echo(f"📁 Created project at {project_path}")

    # Step 2: Init Git
    subprocess.run(["git", "init"], cwd=project_path, stdout=subprocess.DEVNULL)
    click.echo("🔧 Git repo initialised")

    # Step 3: Create venv
    subprocess.run(["python3", "-m", "venv", "venv"], cwd=project_path)
    click.echo("🐍 Virtual environment created")

    # Step 4: Install base requirements
    pip_path = os.path.join(project_path, "venv", "bin", "pip")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], cwd=project_path)
    click.echo("📦 Base requirements installed")

    # Step 5: Install DB driver
    db_driver = None
    if db == "mysql":
        db_driver = "mysql-connector-python"
    elif db == "postgres":
        db_driver = "psycopg2-binary"

    if db_driver:
        subprocess.run([pip_path, "install", db_driver], cwd=project_path)
        click.echo(f"🔌 Installed DB driver: {db_driver}")

    # Step 6: Create .env file
    env_path = os.path.join(project_path, ".env")
    with open(env_path, "w") as env_file:
        if db == "sqlite":
            env_file.write("DB_ENGINE=sqlite\nDB_NAME=database.db\n")
        elif db == "mysql":
            env_file.write(
                "DB_ENGINE=mysql\n"
                "DB_HOST=127.0.0.1\n"
                "DB_PORT=3306\n"
                "DB_NAME=flaskion\n"
                "DB_USER=root\n"
                "DB_PASSWORD=secret\n"
            )
        elif db == "postgres":
            env_file.write(
                "DB_ENGINE=postgres\n"
                "DB_HOST=127.0.0.1\n"
                "DB_PORT=5432\n"
                "DB_NAME=flaskion\n"
                "DB_USER=postgres\n"
                "DB_PASSWORD=secret\n"
            )

    # Step 7: Create default migrations/ folder
    migrations_path = os.path.join(project_path, "migrations")
    os.makedirs(migrations_path, exist_ok=True)
    click.echo("📂 Created migrations/ folder")

    # Step 8: Create .flaskenv for Flask CLI support
    flaskenv_path = os.path.join(project_path, ".flaskenv")
    with open(flaskenv_path, "w") as flaskenv:
        flaskenv.write("FLASK_APP=run.py\nFLASK_ENV=development\n")
    click.echo("⚙️  Created .flaskenv file for flask CLI")

    click.echo(f"📝 .env file created for {db} database\n")
    click.echo(f"✅ Flaskion project '{project_name}' created successfully!\n")
    click.echo(f"🚀 cd {project_name}\n   source venv/bin/activate\n   flask run")


@cli.command(name="make:model")
@click.argument("name")
def make_model(name):
    """
        Generate a new SQLAlchemy model.

        This will create:
        • A model file in app/models/
        • A basic model class with an auto-incrementing ID

        Example:
            flaskion make:model user
    """
    model_name = name.capitalize()
    table_name = name.lower() + "s"

    template_dir = os.path.join(os.path.dirname(__file__), "cli_templates")
    output_dir = os.path.join(os.getcwd(), "app", "models")
    output_file = os.path.join(output_dir, f"{name.lower()}.py")

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("model_template.py.jinja")
    rendered = template.render(model_name=model_name, table_name=table_name)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(rendered)

    click.echo(f"✅ Created model: {output_file}")


@cli.command(name="make:controller")
@click.argument("name")
def make_controller(name):
    """
        Generate a new controller class.

        This creates:
        • A controller in app/controllers/
        • With static methods: index, create, show, update, delete
        • Using Flask's render_template flow

        Example:
            flaskion make:controller UserController
    """
    controller_name = name if name.endswith("Controller") else f"{name.capitalize()}Controller"
    resource_name = name.lower().replace("controller", "")
    resource_name_plural = resource_name + "s"

    template_dir = os.path.join(os.path.dirname(__file__), "cli_templates")
    output_dir = os.path.join(os.getcwd(), "app", "controllers")
    output_file = os.path.join(output_dir, f"{resource_name}_controller.py")

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("controller_template.py.jinja")
    rendered = template.render(
        controller_name=controller_name,
        resource_name=resource_name,
        resource_name_plural=resource_name_plural
    )

    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(rendered)

    click.echo(f"✅ Created controller: {output_file}")


@cli.command(name="make:schema")
@click.argument("name")
def make_schema(name):
    """
        Generate a new Marshmallow schema.

        This creates:
        • A schema in app/schemas/
        • Based on the SQLAlchemy model of the same name

        Example:
            flaskion make:schema user
    """
    model_name = name.capitalize()
    model_name_lower = name.lower()

    template_dir = os.path.join(os.path.dirname(__file__), "cli_templates")
    output_dir = os.path.join(os.getcwd(), "app", "schemas")
    output_file = os.path.join(output_dir, f"{model_name_lower}_schema.py")

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("schema_template.py.jinja")
    rendered = template.render(
        model_name=model_name,
        model_name_lower=model_name_lower
    )

    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(rendered)

    click.echo(f"✅ Created schema: {output_file}")


@cli.command(name="make:resource")
@click.argument("name")
@click.option("--api", is_flag=True, help="Generate API routes instead of web routes")
def new_mvc(name, api):
    """
    Generate a new MVC resource with:
    
    - SQLAlchemy model
    - Class-based controller with index/create/show/update/delete
    - Marshmallow schema
    - Route definitions (appended to web_routes.py or api_routes.py)

    Example:
        flaskion make:resource user
        flaskion make:resource product --api
    """
    model_name = name.capitalize()
    resource_name = name.lower()
    resource_name_plural = resource_name + "s"
    controller_name = f"{model_name}Controller"

    template_dir = os.path.join(os.path.dirname(__file__), "cli_templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    # Paths
    model_file = os.path.join("app", "models", f"{resource_name}.py")
    controller_file = os.path.join("app", "controllers", f"{resource_name}_controller.py")
    schema_file = os.path.join("app", "schemas", f"{resource_name}_schema.py")
    route_file = os.path.join("app", "routes", "api_routes.py" if api else "web_routes.py")

    # --- Generate Model ---
    model_template = env.get_template("model_template.py.jinja")
    with open(model_file, "w") as f:
        f.write(model_template.render(model_name=model_name, table_name=resource_name_plural))
    click.echo(f"✅ Created model: {model_file}")

    # --- Generate Controller ---
    controller_template = env.get_template("controller_template.py.jinja")
    with open(controller_file, "w") as f:
        f.write(controller_template.render(
            controller_name=controller_name,
            resource_name=resource_name,
            resource_name_plural=resource_name_plural
        ))
    click.echo(f"✅ Created controller: {controller_file}")

    # --- Generate Schema ---
    schema_template = env.get_template("schema_template.py.jinja")
    with open(schema_file, "w") as f:
        f.write(schema_template.render(model_name=model_name, model_name_lower=resource_name))
    click.echo(f"✅ Created schema: {schema_file}")

    # --- Append Routes ---
    route_template = env.get_template("api_route_template.py.jinja" if api else "web_route_template.py.jinja")
    route_code = route_template.render(
        controller_name=controller_name,
        resource_name=resource_name,
        resource_name_plural=resource_name_plural
    )

    os.makedirs(os.path.dirname(route_file), exist_ok=True)

    if not os.path.exists(route_file):
        with open(route_file, "w") as f:
            f.write("from flask import Blueprint\n\n")
            f.write(f"{'api' if api else 'web'}_routes = Blueprint('{resource_name}_routes', __name__)\n\n")

    # Add import if not already there
    with open(route_file, "r+") as f:
        contents = f.read()
        import_line = f"from app.controllers.{resource_name}_controller import {controller_name}"
        if import_line not in contents:
            f.seek(0, 0)
            f.write(import_line + "\n" + contents)

    # Append routes
    with open(route_file, "a") as f:
        f.write("\n" + route_code.strip() + "\n")
    click.echo(f"✅ Updated routes in: {route_file}")



@cli.command(name="make:auth")
def make_auth():
    """
    Scaffold authentication system with:
    - User model + schema
    - Auth controller (login, register, logout, dashboard)
    - HTML templates for views
    - Route injection into web_routes.py
    """

    base = os.getcwd()
    env = get_template_env()

    # === File Paths ===
    model_path = os.path.join(base, "app", "models", "user.py")
    schema_path = os.path.join(base, "app", "schemas", "user_schema.py")
    controller_path = os.path.join(base, "app", "controllers", "auth_controller.py")
    template_path = os.path.join(base, "app", "templates", "auth")
    route_file = os.path.join(base, "app", "routes", "web_routes.py")

    os.makedirs(template_path, exist_ok=True)

    # === Render Files ===
    with open(model_path, "w") as f:
        f.write(env.get_template("user_model_template.py.jinja").render())
    click.echo(f"✅ Created model: {model_path}")

    with open(schema_path, "w") as f:
        f.write(env.get_template("user_schema_template.py.jinja").render())
    click.echo(f"✅ Created schema: {schema_path}")

    with open(controller_path, "w") as f:
        f.write(env.get_template("auth_controller_template.py.jinja").render())
    click.echo(f"✅ Created controller: {controller_path}")

    # === HTML Templates ===
    for page in ["login", "register", "dashboard"]:
        html_file = os.path.join(template_path, f"{page}.html")
        jinja_template = f"html/auth/{page}.html.jinja"

        # Read raw content and write as-is
        with importlib.resources.open_text("flaskion_cli.cli_templates", jinja_template) as template_file:
            content = template_file.read()

        with open(html_file, "w") as f:
            f.write(content)

        click.echo(f"✅ Created template: {html_file}")

    # === Update web_routes.py ===
    import_line = "from app.controllers.auth_controller import AuthController"
    routes_block = f"""
web_routes.add_url_rule("/login", view_func=AuthController.login, methods=["GET", "POST"])
web_routes.add_url_rule("/register", view_func=AuthController.register, methods=["GET", "POST"])
web_routes.add_url_rule("/logout", view_func=AuthController.logout)
web_routes.add_url_rule("/dashboard", view_func=AuthController.dashboard)
"""

    if not os.path.exists(route_file):
        os.makedirs(os.path.dirname(route_file), exist_ok=True)
        with open(route_file, "w") as f:
            f.write("from flask import Blueprint\n\n")
            f.write("web_routes = Blueprint('web_routes', __name__)\n\n")

    with open(route_file, "r+") as f:
        content = f.read()
        if import_line not in content:
            f.seek(0, 0)
            f.write(import_line + "\n" + content)

    with open(route_file, "a") as f:
        f.write("\n" + routes_block.strip() + "\n")
    click.echo(f"✅ Routes added to {route_file}")

    click.echo("🚀 Flaskion Auth scaffolding complete! 🎉")

if __name__ == "__main__":
    cli()