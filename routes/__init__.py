"""
Routes package for GreenHarvest Farm Management System.
"""


def register_routes(app):
    """Register all route blueprints with the Flask app."""
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.expenses import expenses_bp
    from routes.health_records import health_bp
    from routes.income import income_bp
    from routes.inventory import inventory_bp
    from routes.livestock import livestock_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(livestock_bp)
