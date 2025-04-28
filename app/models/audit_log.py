import uuid
from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'))
    actor_user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    action_type = db.Column(db.String(64), nullable=False)
    target_type = db.Column(db.String(64))
    target_id = db.Column(db.String(36))
    meta = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships temporarily removed for migration
    # Will be added back after migration
    # customer = db.relationship('Customer', back_populates='audit_logs')
    # actor_user = db.relationship('User')
