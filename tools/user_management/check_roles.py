from app import create_app
from app.models import Role
from app.extensions import db

app = create_app()

def check_roles():
    with app.app_context():
        roles = Role.query.all()
        print(f"Total roles: {len(roles)}")
        
        for role in roles:
            print(f"Role ID: {role.id}, Name: {role.name}, Description: {role.description}")
            print("-" * 50)

if __name__ == "__main__":
    check_roles() 