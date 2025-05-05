import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = "your-secret-key"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL",
                                        "mysql+pymysql://root@localhost:3306/airo-sales")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")