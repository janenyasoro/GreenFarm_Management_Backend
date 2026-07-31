from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, jwt, bcrypt, cors
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            "origins": [
                "http://localhost:5173", 
                "http://localhost:3000", 
                "http://127.0.0.1:5173",
                os.environ.get('FRONTEND_ORIGIN', 'https://starfish-app-qjq8s.ondigitalocean.app'),
                "https://starfish-app-qjq8s.ondigitalocean.app"
            ],
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

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(crops_bp, url_prefix='/api/crops')
    app.register_blueprint(livestock_bp, url_prefix='/api/livestock')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    app.register_blueprint(income_bp, url_prefix='/api/income')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        logger.info("Health check endpoint called")
        return jsonify({
            "status": "ok", 
            "service": "GreenHarvest API",
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "version": "1.0.0"
        })

    # Root endpoint to verify API is running
    @app.route('/api', methods=['GET'])
    def api_root():
        return jsonify({
            "message": "GreenHarvest API is running",
            "endpoints": [
                "/api/health",
                "/api/auth/login",
                "/api/auth/register",
                "/api/auth/profile",
                "/api/crops",
                "/api/livestock",
                "/api/health",
                "/api/expenses",
                "/api/income",
                "/api/inventory",
                "/api/tasks",
                "/api/dashboard",
                "/api/admin"
            ]
        })

    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"404 error: {e}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Use PORT from environment variable for production
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)