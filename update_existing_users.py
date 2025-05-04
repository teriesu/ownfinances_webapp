from app import create_app
from app.models import Users
from app.extensions import db
import uuid

app = create_app()

def update_users_with_uniquifier():
    with app.app_context():
        # Get all users that don't have fs_uniquifier set
        users = Users.query.filter(Users.fs_uniquifier.is_(None)).all()
        print(f"Found {len(users)} users without fs_uniquifier")
        
        # Update each user with a new UUID
        for user in users:
            user.fs_uniquifier = str(uuid.uuid4())
            print(f"Setting fs_uniquifier for user {user.user}")
        
        # Commit all changes
        db.session.commit()
        print("All users updated successfully")

if __name__ == "__main__":
    update_users_with_uniquifier() 