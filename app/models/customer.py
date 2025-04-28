import uuid
from datetime import datetime
from app.extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    domain = db.Column(db.String(128))
    admin_user_id = db.Column(db.String(36))
    subdomain_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    plan_type = db.Column(db.Enum('free', 'business', 'enterprise', name='plan_type_enum'), default='free')
    status = db.Column(db.Enum('active', 'suspended', 'deleted', name='customer_status_enum'), default='active')

    # Relationships temporarily removed for migration
    # Will be added back after migration
    # admin_user = db.relationship('User', uselist=False)
    # users = db.relationship('User', back_populates='customer')
    # audit_logs = db.relationship('AuditLog', back_populates='customer')
