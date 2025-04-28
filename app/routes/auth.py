from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User
from app.schemas.user import LoginSchema
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: Login
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: superadmin1@example.com
            password:
              type: string
              example: secret123
    responses:
      200:
        description: Successful login
        schema:
          properties:
            access_token:
              type: string
            user:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                name:
                  type: string
                username:
                  type: string
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    schema = LoginSchema()
    data = request.get_json()
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'customer_id': user.customer_id
            }
        )
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        }), 200
    return jsonify({'error': 'Invalid email or password'}), 401
