from app import create_app
from app.models import Users, Role
from app.extensions import db
from sqlalchemy import text

app = create_app()

def fix_roles_table():
    with app.app_context():
        # Get the admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Admin role not found")
            return
        
        user = Users.query.first()
        if not user:
            print("No users found")
            return
        
        print(f"Checking roles_users table for user {user.id} and role {admin_role.id}")
        
        # Direct SQL to check roles_users table
        sql = text("SELECT * FROM roles_users WHERE user_id = :user_id AND role_id = :role_id")
        result = db.session.execute(sql, {"user_id": user.id, "role_id": admin_role.id})
        rows = result.fetchall()
        
        if rows:
            print(f"Found {len(rows)} entries in roles_users table for this user-role combo")
        else:
            print("No entries found in roles_users table")
            print("Inserting direct entry into roles_users table")
            
            # Insert directly with SQL
            insert_sql = text("INSERT INTO roles_users (user_id, role_id) VALUES (:user_id, :role_id)")
            db.session.execute(insert_sql, {"user_id": user.id, "role_id": admin_role.id})
            db.session.commit()
            print("Direct insertion complete")
        
        # Verify again
        result = db.session.execute(sql, {"user_id": user.id, "role_id": admin_role.id})
        rows = result.fetchall()
        if rows:
            print(f"Verification: Found {len(rows)} entries in roles_users table for this user-role combo")
        else:
            print("Verification: Still no entries in roles_users table - something is wrong")
        
if __name__ == "__main__":
    fix_roles_table() 