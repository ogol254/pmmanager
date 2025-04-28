from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.customer import Customer
from app.models.user import User
import uuid
from datetime import datetime
from flask_jwt_extended import get_jwt

customer_bp = Blueprint('customer', __name__, url_prefix='/api/customers')

@customer_bp.route('', methods=['GET'])
def get_customers():
    """
    Fetch all customers (superadmin only). Other users see only their own customer.
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    responses:
      200:
        description: List of customers
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: string}
              name: {type: string}
              plan_type: {type: string}
              status: {type: string}
              subdomain_url: {type: string}
    """
    claims = get_jwt()
    role = claims.get('role')
    customer_id = claims.get('customer_id')

    if role in ("superadmin", "superadmin_readonly"):
        customers = Customer.query.all()
    else:
        customers = Customer.query.filter_by(id=customer_id).all()

    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'plan_type': c.plan_type,
            'status': c.status,
            'subdomain_url': c.subdomain_url
        } for c in customers
    ])

@customer_bp.route('/<customer_id>/users', methods=['GET'])
def get_customer_users(customer_id):
    """
    Fetch customer users details including admin
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        required: true
        type: string
        example: 7b2f5e5e-6c0a-4f9b-8c7e-123456789abc
    responses:
      200:
        description: List of users for the customer
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: string}
              name: {type: string}
              email: {type: string}
              role: {type: string}
              status: {type: string}
    """
    users = User.query.filter_by(customer_id=customer_id).all()
    return jsonify([
        {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'status': u.status
        } for u in users
    ])

@customer_bp.route('/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Fetch customer details including admin user
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        required: true
        type: string
        example: 7b2f5e5e-6c0a-4f9b-8c7e-123456789abc
    responses:
      200:
        description: Customer details
        schema:
          type: object
          properties:
            id: {type: string}
            name: {type: string}
            plan_type: {type: string}
            status: {type: string}
            subdomain_url: {type: string}
            admin:
              type: object
              properties:
                id: {type: string}
                name: {type: string}
                email: {type: string}
      404:
        description: Customer not found
    """
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    admin = User.query.get(customer.admin_user_id) if customer.admin_user_id else None
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'plan_type': customer.plan_type,
        'status': customer.status,
        'subdomain_url': customer.subdomain_url,
        'admin': {
            'id': admin.id,
            'name': admin.name,
            'email': admin.email
        } if admin else None
    })

@customer_bp.route('/<customer_id>', methods=['PATCH'])
def update_customer(customer_id):
    """
    Update customer settings
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        required: true
        type: string
        example: 7b2f5e5e-6c0a-4f9b-8c7e-123456789abc
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name: {type: string, example: "Acme Inc"}
            plan_type: {type: string, enum: [free, business, enterprise], example: "business"}
    responses:
      200:
        description: Customer updated
      404:
        description: Customer not found
    """
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    data = request.get_json()
    if 'name' in data:
        customer.name = data['name']
    if 'plan_type' in data:
        customer.plan_type = data['plan_type']
    customer.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Customer updated'})

@customer_bp.route('/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """
    Soft delete (suspend) customer account
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        required: true
        type: string
        example: 7b2f5e5e-6c0a-4f9b-8c7e-123456789abc
    responses:
      200:
        description: Customer suspended
      404:
        description: Customer not found
    """
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    customer.status = 'suspended'
    customer.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Customer suspended'})

@customer_bp.route('', methods=['POST'])
def create_customer():
    """
    Create a new customer and first admin user
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            customer_name:
              type: string
              example: Acme Inc
            admin:
              type: object
              properties:
                name:
                  type: string
                  example: John Doe
                email:
                  type: string
                  example: john@acme.com
            plan_type:
              type: string
              enum: [free, business, enterprise]
              example: enterprise
    responses:
      201:
        description: Customer and admin created
        schema:
          type: object
          properties:
            customer_id:
              type: string
              example: 7b2f5e5e-6c0a-4f9b-8c7e-123456789abc
            admin_user_id:
              type: string
              example: 1c2d3e4f-5678-1234-9abc-def012345678
            subdomain_url:
              type: string
              example: https://acme.yourapp.com
    """
    data = request.get_json()
    customer_name = data.get('customer_name')
    admin = data.get('admin', {})
    plan_type = data.get('plan_type', 'free')

    # Generate slug/subdomain
    slug = customer_name.lower().replace(' ', '')
    subdomain_url = f"https://{slug}.yourapp.com"

    # Prevent duplicate slugs
    if Customer.query.filter_by(slug=slug).first():
        return jsonify({'error': f'Customer with slug "{slug}" already exists.'}), 400

    # Create Customer
    customer = Customer(
        id=str(uuid.uuid4()),
        name=customer_name,
        slug=slug,
        domain=subdomain_url,
        subdomain_url=subdomain_url,
        plan_type=plan_type,
        status='active',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(customer)
    db.session.flush()  # Get customer.id before commit

    # Check for duplicate admin email
    if User.query.filter_by(email=admin['email']).first():
        db.session.rollback()
        return jsonify({'error': f'User with email "{admin["email"]}" already exists.'}), 400

    # Create Admin User
    admin_user = User(
        id=str(uuid.uuid4()),
        customer_id=customer.id,
        email=admin['email'],
        name=admin['name'],
        role='admin',
        status='active',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    # Set default password for admin user
    admin_user.set_password('secret123')
    db.session.add(admin_user)
    db.session.flush()

    # Link admin user to customer
    customer.admin_user_id = admin_user.id
    db.session.commit()

    # TODO: Send invitation email to admin_user.email
    # TODO: Provision default settings for the customer

    return jsonify({
        'customer_id': customer.id,
        'admin_user_id': admin_user.id,
        'subdomain_url': subdomain_url
    }), 201
