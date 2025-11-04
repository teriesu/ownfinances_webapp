from app import create_app
from app.models import Users, Role
from app.extensions import db

app = create_app()

def assign_admin_role():
    with app.app_context():
        # Get the admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Admin role not found, creating it")
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
        
        # Get all users
        users = Users.query.all()
        print(f"Found {len(users)} users")
        
        # Assign admin role to each user
        for user in users:
            print(f"Processing user: {user.user}")
            if admin_role not in user.roles:
                user.roles.append(admin_role)
                print(f"  Admin role assigned to {user.user}")
            else:
                print(f"  User {user.user} already has admin role")
        
        # Commit changes
        db.session.commit()
        print("All users updated successfully")

if __name__ == "__main__":
    assign_admin_role() 