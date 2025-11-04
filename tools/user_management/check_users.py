from app import create_app
from app.models import Users
from app.extensions import db

app = create_app()

def check_users():
    with app.app_context():
        users = Users.query.all()
        print(f"Total users: {len(users)}")
        
        for user in users:
            print(f"User ID: {user.id}, Username: {user.user}, Email: {user.email}")
            print(f"  fs_uniquifier: {user.fs_uniquifier}")
            print(f"  active: {user.active}")
            print(f"  roles: {user.roles}")
            print("-" * 50)

if __name__ == "__main__":
    check_users() 