from flask import Flask, jsonify, request
from app.config import settings
from app.extensions import db, migrate, swagger
from app.routes.user import user_bp
from app.routes.auth import auth_bp
from app.routes.customer import customer_bp
from flask_jwt_extended import JWTManager
from app.models import User


def create_app(config_class=settings.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    # Add Swagger Bearer token security definition
    from app.utils.swagger_definitions import swagger_definitions
    app.config['SWAGGER'] = {
        'uiversion': 3,
        'basePath': '',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
            }
        },
        'security': [{'Bearer': []}],
        'tags': [
            {'name': 'Auth', 'description': 'Authentication operations'},
            {'name': 'Users', 'description': 'User management operations'}
        ],
        'specs': [
            {
                'endpoint': 'apispec',
                'route': '/apispec.json',
                'model_filter': lambda tag: True,
            }
        ],
        'specs_route': '/apidocs/',
        'definitions': swagger_definitions,
    }
    app.config['SWAGGER']['lazy'] = True

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp)
    app.register_blueprint(customer_bp)

    # Now, initialize swagger (after blueprints)
    swagger.init_app(app)

    from app.middleware import validate_session_and_scope
    
    # Apply middleware globally except for auth endpoints
    @app.before_request
    def enforce_tenant_scope():
        # Allow Swagger UI and OpenAPI spec endpoints to bypass tenant/session middleware
        if request.path.startswith('/apidocs') or request.path.startswith('/apispec.json'):
            return
        # Only enforce for /api/users and /api/customers endpoints
        if request.path.startswith('/api/users') or request.path.startswith('/api/customers'):
            resp = validate_session_and_scope()(lambda: None)()
            if resp is not None:
                return resp



    # Create super admin if not exists (using permissions column)
    # Temporarily commented out for migration
    from scripts.create_first_user import create_first_admin
    create_first_admin(app)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method Not Allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500

    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome to ProjectManager API'})

    return app
