from app import create_app
from app.extensions import db
from app.models import User

# This script creates the first user (admin) if not already present

def create_first_admin(app=None):
    from app.extensions import db
    from app.models import User
    if app is None:
        from app import create_app
        app = create_app()
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='superadmin2@example.com').first():
            user = User(
                email='superadmin2@example.com',
                name='Super Admin',
                role='superadmin',        # or your admin role value
                status='active',     # or your default active status value
            )
            user.set_password('secret123')
            db.session.add(user)
            db.session.commit()
            print('Super admin created!')
        else:
            print('Super admin already exists.')

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    create_first_admin(app)
