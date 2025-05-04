from app import create_app
from app.models import Users
from app.extensions import db
import uuid

app = create_app()

def update_users_uniquifier():
    with app.app_context():
        # Get all users
        users = Users.query.all()
        print(f"Found {len(users)} users")
        
        # Update each user with a new UUID if needed
        updated_count = 0
        for user in users:
            if not user.fs_uniquifier:
                user.fs_uniquifier = str(uuid.uuid4())
                updated_count += 1
                print(f"Setting fs_uniquifier for user {user.user}: {user.fs_uniquifier}")
            else:
                print(f"User {user.user} already has fs_uniquifier: {user.fs_uniquifier}")
        
        # Commit all changes
        if updated_count > 0:
            db.session.commit()
            print(f"Updated {updated_count} users with new fs_uniquifier values")
        else:
            print("No users needed updating")

if __name__ == "__main__":
    update_users_uniquifier() 