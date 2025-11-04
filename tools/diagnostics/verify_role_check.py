from app import create_app
from app.models import Users, Role
from app.extensions import role_required
from flask_login import current_user
import inspect

app = create_app()

def verify_role_check():
    with app.app_context():
        # Get user and role
        user = Users.query.filter_by(id=3).first()
        admin_role = Role.query.filter_by(name='admin').first()
        
        if not user:
            print("User with ID 3 not found")
            return
        
        if not admin_role:
            print("Admin role not found")
            return
        
        print(f"User: {user.user}, Roles: {user.roles}")
        print(f"Admin role: {admin_role.name}, ID: {admin_role.id}")
        
        # Check if user has admin role
        has_admin = any(role.name == 'admin' for role in user.roles)
        print(f"User has admin role: {has_admin}")
        
        # Manually check role_required logic
        for role in user.roles:
            print(f"Role check: User role '{role.name}' in ['admin']: {role.name in ['admin']}")
        
        # Show the role_required implementation
        print("\nRole required implementation:")
        print(inspect.getsource(role_required))

if __name__ == "__main__":
    verify_role_check() 