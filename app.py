import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///greenfarm.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-me-in-production")

    from extensions import db, bcrypt, jwt, migrate
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.tasks import tasks_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
