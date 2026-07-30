from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, jwt, bcrypt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Configure CORS - allow frontend origins
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Import models so Flask-Migrate can detect them
    import models  # noqa: F401

    # Register blueprints
    from routes.auth import auth_bp
    from routes.crops import crops_bp
    from routes.livestock import livestock_bp
    from routes.health_records import health_bp
    from routes.expenses import expenses_bp
    from routes.income import income_bp
    from routes.inventory import inventory_bp
    from routes.tasks import tasks_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(livestock_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "service": "GreenHarvest API"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
