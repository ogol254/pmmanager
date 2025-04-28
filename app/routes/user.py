from app.extensions import db
from app.models import User
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from app.schemas.user import UserSchema

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/test', methods=['GET'])
def test_user():
    """
    Test endpoint
    ---
    tags:
      - Users
    responses:
      200:
        description: OK
    """
    return jsonify({'ok': True})

# Role enforcement helpers
ROLES = {
    'ADMIN': 'admin',
    'MANAGER': 'manager',
    'USER': 'user',
    'VIEWER': 'viewer',
    'SUPERADMIN': 'superadmin',
    'SUPERADMIN_READONLY': 'superadmin_readonly'
}

def is_admin(role):
    return role == ROLES['ADMIN']

def is_manager(role):
    return role == ROLES['MANAGER']

def is_superadmin(role):
    return role == ROLES['SUPERADMIN']

def is_superadmin_readonly(role):
    return role == ROLES['SUPERADMIN_READONLY']

@user_bp.route('/list', methods=['GET'])
@jwt_required()
def get_users():
    """
    Get all users
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
              email:
                type: string
              name:
                type: string
              role:
                type: string
              status:
                type: string
    """
    # Enforce customer_id from JWT
    claims = get_jwt()
    customer_id = claims.get('customer_id')
    users = User.query.filter_by(customer_id=customer_id).all()
    schema = UserSchema(many=True)
    return jsonify(schema.dump(users))

@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get user by ID
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        example: 2b26ae13-51c0-45e7-9adf-411d8c482ce3
    responses:
      200:
        description: User object
        schema:
          properties:
            id:
              type: integer
            email:
              type: string
            name:
              type: string
            role:
              type: string
            status:
              type: string
      404:
        description: User not found
    """
    # Enforce customer_id from JWT
    claims = get_jwt()
    customer_id = claims.get('customer_id')
    user = User.query.get(user_id)
    if not user or user.customer_id != customer_id:
        return jsonify({'error': 'User not found'}), 404
    schema = UserSchema()
    return jsonify(schema.dump(user))

@user_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """
    Create a new user (admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: superadmin@example.com
            name:
              type: string
              example: Super Admin
            password:
              type: string
              example: secret123
            role:
              type: string
              enum: ['admin', 'manager', 'user', 'viewer']
              example: user
            status:
              type: string
              example: active
            invitation_token:
              type: string
            last_login_at:
              type: string
    responses:
      201:
        description: User created
        schema:
          properties:
            id:
              type: integer
            email:
              type: string
            name:
              type: string
            role:
              type: string
            status:
              type: string
            invitation_token:
              type: string
            last_login_at:
              type: string
    """
    # Enforce customer_id from JWT
    claims = get_jwt()
    current_user = User.query.get(get_jwt_identity())
    customer_id = claims.get('customer_id')
    role = claims.get('role')
    # Only allow Admins to invite users (per matrix)
    if not current_user or not is_admin(role):
        return jsonify({'error': 'Only admins can invite users'}), 403
    if is_superadmin_readonly(role):
        return jsonify({'error': 'Read-only role cannot invite users'}), 403
    schema = UserSchema()
    try:
        user_data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    # Always use customer_id from JWT
    if User.query.filter(User.email == user_data['email'], User.customer_id == customer_id).first():
        return jsonify({'error': 'User with that email already exists in this tenant'}), 400
    user = User(
        email=user_data['email'],
        name=user_data['name'],
        role=user_data.get('role', 'user'),
        status=user_data.get('status', 'active'),
        customer_id=customer_id,
        invitation_token=user_data.get('invitation_token'),
        last_login_at=user_data.get('last_login_at'),
    )
    user.set_password(user_data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(schema.dump(user)), 201

@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update a user (admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        example: 2b26ae13-51c0-45e7-9adf-411d8c482ce3
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
            name:
              type: string
              example: John Doe
            password:
              type: string
              example: secret123
            role:
              type: string
              enum: [admin, manager, user, viewer]
              example: user
            status:
              type: string
              example: active
            invitation_token:
              type: string
            last_login_at:
              type: string
    responses:
      200:
        description: User updated
      403:
        description: Forbidden
      404:
        description: User not found
      400:
        description: Validation error
    """
    # Enforce customer_id from JWT
    claims = get_jwt()
    current_user = User.query.get(get_jwt_identity())
    customer_id = claims.get('customer_id')
    role = claims.get('role')
    # Only Admin or Manager can update users in their tenant
    if is_superadmin_readonly(role):
        return jsonify({'error': 'Read-only role cannot update users'}), 403
    if not current_user or not (is_admin(role) or is_manager(role)):
        return jsonify({'error': 'Only admins or managers can update users'}), 403
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    user = User.query.get(user_id)
    if not user or user.customer_id != customer_id:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing fields'}), 400
    for field in ('email', 'name', 'role', 'status', 'invitation_token', 'last_login_at'):
        if field in data:
            setattr(user, field, data[field])
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    schema = UserSchema()
    return jsonify(schema.dump(user))

@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete a user (admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        example: 2b26ae13-51c0-45e7-9adf-411d8c482ce3
    responses:
      200:
        description: User deleted
      403:
        description: Forbidden
      404:
        description: User not found
    """
    # Enforce customer_id from JWT
    claims = get_jwt()
    current_user = User.query.get(get_jwt_identity())
    customer_id = claims.get('customer_id')
    role = claims.get('role')
    # Only Admin or Manager can delete users in their tenant
    if is_superadmin_readonly(role):
        return jsonify({'error': 'Read-only role cannot delete users'}), 403
    if not current_user or not (is_admin(role) or is_manager(role)):
        return jsonify({'error': 'Only admins or managers can delete users'}), 403
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    if current_user.id == user_id:
        return jsonify({'error': 'Admin users cannot delete their own account'}), 400
    user = User.query.get(user_id)
    if not user or user.customer_id != customer_id:
        return jsonify({'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})
