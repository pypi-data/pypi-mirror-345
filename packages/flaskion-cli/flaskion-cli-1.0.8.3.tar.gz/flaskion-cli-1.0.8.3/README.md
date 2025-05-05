# Flaskion

Flaskion is a lightweight MVC boilerplate for Flask, providing developers with a **structured foundation** for Flask applications. Inspired by Laravel, Flaskion brings **modular architecture**, **scalability**, and a **clean codebase** to Flask projects.

---

## **Features**
✅ **MVC Architecture** – Clear separation of concerns with `controllers`, `models`, and `templates`.  
✅ **Centralized Routing** – Web and API routes are separated for better organization.  
✅ **Built-in CLI** – Generate new Flaskion projects instantly with `flaskion new {projectname}`.  
✅ **Scalability** – Pre-configured to integrate with Flask extensions like SQLAlchemy, Flask-Migrate, and more.  
✅ **Reusability** – Easily adaptable for any Flask project.  

---

## Project Structure
```
flaskion/
├── app/
│   ├── init.py         # Application factory
│   ├── routes/             # Folder for all routes
│   │   ├── web_routes.py   # Routes for web views
│   │   ├── api_routes.py   # Routes for APIs
│   ├── controllers/ 
|   |── schemas/            # Database Schemas
│   ├── models/             # Database models
│   ├── templates/          # HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   └── config.py           # Configuration
├── run.py                  # Entry point
├── requirements.txt        # Dependencies
├── .env.example            # Enviroment File
└── README.md               # Documentation
```

---

## Getting Started

### Installation

1. Install Flaskion CLI** (if not installed):
   ```bash
   pip install flaskion-cli
    ```
2.	Create a new Flaskion project:
   ```bash
   flaskion new myproject
   ```
3. Navigate into your new project:
   ```bash
   cd myproject
   ```
4. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
## Managing Routes

Flaskion organizes routes into a dedicated routes/ folder, separating Web Routes and API Routes.
	•	Web Routes (routes/web_routes.py)
Defines routes for pages that return HTML views.
	•	API Routes (routes/api_routes.py)
Handles JSON-based API requests.

Both are registered inside app/__init__.py:
```python
from flask import Flask
from app.routes.api_routes import api_routes
from app.routes.web_routes import web_routes

def register_routes(app: Flask):
    app.register_blueprint(api_routes)
    app.register_blueprint(web_routes)
```

## Running the App
1. Start the Flask development server:
    ```bash
    flask run --debug
   ```
2. Visit the app in your browser:
http://127.0.0.1:5000


## Documentation
Coming Soon