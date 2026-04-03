Perfect! Here's how to access the database directly and run SQL commands:

## 🗄️ Direct PostgreSQL Access

### Connect to PostgreSQL Shell

```bash
docker-compose exec db psql -U postgres -d personalfinances
```

This will give you a PostgreSQL prompt where you can run SQL commands directly.

### Common SQL Commands

Once you're in the PostgreSQL shell (`personalfinances=#`), you can use:

#### View Database Structure
```sql
-- List all tables
\dt

-- Describe a specific table structure
\d users
\d gastos
\d ingresos

-- List all tables with sizes
\dt+
```

#### Query Data
```sql
-- View all users
SELECT * FROM users;

-- View specific columns
SELECT id, user, email, active FROM users;

-- Count records
SELECT COUNT(*) FROM users;

-- Filter data
SELECT * FROM users WHERE active = true;

-- Join tables (if needed)
SELECT u.user, r.name 
FROM users u 
JOIN roles_users ru ON u.id = ru.user_id 
JOIN role r ON ru.role_id = r.id;
```

#### Insert Data
```sql
-- Insert a new user (example - adjust columns to match your table)
INSERT INTO users (user, email, password, active) 
VALUES ('newuser', 'user@example.com', 'hashed_password', true);

-- Insert and return the created record
INSERT INTO users (user, email, password, active) 
VALUES ('testuser', 'test@example.com', 'pass123', true) 
RETURNING *;
```

#### Update Data
```sql
-- Update a user's email
UPDATE users 
SET email = 'newemail@example.com' 
WHERE user = 'username';

-- Update multiple fields
UPDATE users 
SET email = 'new@email.com', active = true 
WHERE id = 1;

-- Update with confirmation
UPDATE users 
SET email = 'updated@example.com' 
WHERE user = 'username' 
RETURNING *;
```

#### Delete Data
```sql
-- Delete a specific user
DELETE FROM users 
WHERE user = 'olduser';

-- Delete with condition
DELETE FROM users 
WHERE active = false;

-- Delete and see what was deleted
DELETE FROM users 
WHERE user = 'testuser' 
RETURNING *;
```

#### Transaction Control
```sql
-- Start a transaction (to test before committing)
BEGIN;

-- Run your SQL command
UPDATE users SET email = 'test@example.com' WHERE user = 'testuser';

-- Check the result
SELECT * FROM users WHERE user = 'testuser';

-- If it looks good, commit
COMMIT;

-- Or if you made a mistake, rollback
ROLLBACK;
```

### PostgreSQL Shell Commands

```sql
-- Get help
\h           -- SQL command help
\?           -- PostgreSQL command help

-- Database info
\l           -- List all databases
\dt          -- List tables
\d tablename -- Describe table structure
\du          -- List users/roles

-- Navigation
\c dbname    -- Connect to different database
\q           -- Quit/exit

-- Output formatting
\x           -- Toggle expanded display (useful for wide tables)
\x auto      -- Auto-expand when needed

-- Execute SQL from file
\i /path/to/file.sql
```

### Example Session

Here's a complete example of what you might do:

```bash
# 1. Connect to database
docker-compose exec db psql -U postgres -d personalfinances

# Now you're in the PostgreSQL shell:

# 2. See what tables exist
\dt

# 3. Check the structure of users table
\d users

# 4. View all users
SELECT * FROM users;

# 5. Update a user (in a transaction)
BEGIN;
UPDATE users SET email = 'newemail@example.com' WHERE user = 'myusername';
SELECT * FROM users WHERE user = 'myusername';  -- Verify
COMMIT;

# 6. Exit
\q
```

### Quick One-Liner Queries

You can also run single queries without entering the shell:

```bash
# Run a single query
docker-compose exec db psql -U postgres -d personalfinances -c "SELECT * FROM users;"

# Count users
docker-compose exec db psql -U postgres -d personalfinances -c "SELECT COUNT(*) FROM users;"

# Update and see result
docker-compose exec db psql -U postgres -d personalfinances -c "UPDATE users SET active=true WHERE user='testuser' RETURNING *;"
```

### Pro Tips

1. **Use transactions** for safety:
   ```sql
   BEGIN;
   -- your changes
   -- check them
   COMMIT;  -- or ROLLBACK if wrong
   ```

2. **Use expanded display** for wide tables:
   ```sql
   \x
   SELECT * FROM users WHERE id = 1;
   ```

3. **Save output to file** (from your terminal):
   ```bash
   docker-compose exec db psql -U postgres -d personalfinances -c "SELECT * FROM users;" > users_backup.txt
   ```

4. **Execute SQL file**:
   ```bash
   docker-compose exec -T db psql -U postgres -d personalfinances < my_updates.sql
   ```

### Need to Back Up First?

Before making changes, create a backup:

```bash
# Full database backup
docker-compose exec -T db pg_dump -U postgres personalfinances > backup_before_changes.sql

# Or just one table
docker-compose exec -T db pg_dump -U postgres -t users personalfinances > users_backup.sql
```

That's it! You now have direct SQL access to your database. Just run `docker-compose exec db psql -U postgres -d personalfinances` and start typing SQL commands.


Here’s a practical split for your project.

## Most code changes (Python, templates, static files)

You **do not** need to rebuild the image. The dev stack mounts your project (`.:/app`) and Flask reloads in debug mode.

- **Do nothing** — save the file and wait for the “Detected change … reloading” line in the logs, **or**
- **Restart only the web service** if something looks stuck:

```bash
docker-compose restart web
```

## When you **must** rebuild the image

Rebuild when you change anything that defines the container itself, for example:

- `Dockerfile` / `Dockerfile.prod`
- `requirements.txt` / `requirements.prod.txt`
- `docker-compose.yml` (e.g. new packages in `RUN apt-get`, env, command)
- System packages / locale steps in the Dockerfile

Then:

```bash
docker-compose up -d --build
```

That rebuilds images and recreates containers as needed.

**Optional:** force a clean recreate (same compose file):

```bash
docker-compose up -d --build --force-recreate
```

## If you use the Makefile

```bash
make rebuild
```

(That’s the shortcut your project added for “rebuild and restart”.)

## Production compose

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**Summary:** day-to-day edits → usually **restart web** or rely on reload; **Dockerfile / requirements / compose** changes → **`docker-compose up -d --build`**.