"""
Flask application factory for GreenHarvest Farm Management System.
"""
import os
from flask import Flask, jsonify
from config import config
from extensions import init_extensions, db, jwt
from routes import register_routes


# In-memory token blocklist for logout functionality
# In production, use Redis or a database-backed store
revoked_tokens = set()


def create_app(config_name=None):
    """
    Application factory function.

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)

    # Register routes
    register_routes(app)

    # Register error handlers
    register_error_handlers(app)

    # Register JWT callbacks
    register_jwt_callbacks(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


def register_error_handlers(app):
    """Register custom error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'You do not have permission to perform this action.'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


def register_jwt_callbacks(app):
    """Register JWT callbacks for token blocklist and error handling."""

    # Only register blocklist callbacks if enabled
    if app.config.get('JWT_BLACKLIST_ENABLED'):
        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            """Check if a token has been revoked (added to blocklist)."""
            jti = jwt_payload['jti']
            return jti in revoked_tokens

        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            """Handle revoked token errors."""
            return jsonify({
                'success': False,
                'detail': 'The token has been revoked.'
            }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token errors."""
        return jsonify({
            'success': False,
            'detail': 'The token has expired.'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        """Handle invalid token errors."""
        return jsonify({
            'success': False,
            'detail': 'Invalid token.'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        """Handle missing token errors."""
        return jsonify({
            'success': False,
            'detail': 'Authentication credentials were not provided.'
        }), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        """Handle needs fresh token errors."""
        return jsonify({
            'success': False,
            'detail': 'Fresh token required.'
        }), 401


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
