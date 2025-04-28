from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(36))
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Enum('superadmin', 'superadmin_readonly', 'admin', 'manager', 'user', 'viewer', name='user_role_enum'), default='user')
    status = db.Column(db.Enum('active', 'pending', 'suspended', name='user_status_enum'), default='active')
    password_hash = db.Column(db.String(256))
    invitation_token = db.Column(db.String(128))
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship temporarily removed for migration
    # Will be added back after migration
    # customer = db.relationship('Customer', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
