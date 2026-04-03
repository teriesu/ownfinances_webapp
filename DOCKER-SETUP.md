# Docker Setup Guide for WSL2

You need to set up Docker to run this application. Here are your options:

## Option 1: Docker Desktop with WSL2 Integration (Recommended for Windows)

This is the easiest option if you're on Windows with WSL2.

### Steps:

1. **Install Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop
   - Run the installer
   - During installation, ensure "Use WSL 2 instead of Hyper-V" is selected

2. **Enable WSL2 Integration**
   - Open Docker Desktop
   - Go to Settings → Resources → WSL Integration
   - Enable integration with your WSL2 distro (Ubuntu, etc.)
   - Click "Apply & Restart"

3. **Verify Installation in WSL**
   ```bash
   docker --version
   docker-compose --version
   ```

4. **Run the Application**
   ```bash
   ./start-docker.sh
   ```

## Option 2: Docker Engine on WSL2 (Direct Installation)

If you prefer not to use Docker Desktop, you can install Docker directly in WSL2.

### Steps:

1. **Update packages**
   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg lsb-release
   ```

2. **Add Docker's official GPG key**
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```

3. **Set up the repository**
   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

4. **Install Docker Engine**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

5. **Start Docker service**
   ```bash
   sudo service docker start
   ```

6. **Add your user to docker group (optional, to run without sudo)**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

7. **Verify installation**
   ```bash
   docker --version
   docker compose version
   ```

8. **Make Docker start automatically (add to ~/.bashrc)**
   ```bash
   echo 'sudo service docker start > /dev/null 2>&1' >> ~/.bashrc
   ```

9. **Run the Application**
   ```bash
   ./start-docker.sh
   ```

## Option 3: Run Without Docker (Direct PostgreSQL)

If you don't want to use Docker, you can install PostgreSQL directly in Windows or WSL.

### For Windows (PostgreSQL on Windows, Flask in WSL):

1. **Install PostgreSQL on Windows**
   - Download from: https://www.postgresql.org/download/windows/
   - Install with default settings
   - Remember the password you set for the `postgres` user

2. **Update your `.env` file**
   ```bash
   # Find your Windows host IP
   cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
   
   # Update DB_HOST in .env with that IP (usually 172.x.x.x or similar)
   nano .env
   ```

3. **Run the Flask app**
   ```bash
   source venv/bin/activate
   flask run
   ```

### For WSL (PostgreSQL in WSL):

1. **Install PostgreSQL**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Start PostgreSQL**
   ```bash
   sudo service postgresql start
   ```

3. **Create database and user**
   ```bash
   sudo -u postgres psql
   ```
   
   Then in PostgreSQL prompt:
   ```sql
   CREATE USER postgres WITH PASSWORD '10_tellez';
   CREATE DATABASE personalfinances;
   GRANT ALL PRIVILEGES ON DATABASE personalfinances TO postgres;
   \q
   ```

4. **Update `.env`**
   ```bash
   DB_HOST=localhost
   ```

5. **Run the Flask app**
   ```bash
   source venv/bin/activate
   flask db upgrade
   flask run
   ```

## Recommendation

For the best development experience, I recommend **Option 1 (Docker Desktop)** because:
- ✅ Easy to set up
- ✅ Works great with WSL2
- ✅ Consistent across different machines
- ✅ Easy to share with team members
- ✅ One-command deployment

## Next Steps

After choosing and setting up your preferred option:

1. Follow the setup instructions above
2. Return to [QUICKSTART.md](QUICKSTART.md) to start the application
3. Access the app at http://localhost:616

## Need Help?

If you encounter issues:

1. **Docker Desktop not connecting to WSL?**
   - Make sure WSL2 is your default version: `wsl --set-default-version 2`
   - Restart Docker Desktop
   - Check Docker Desktop → Settings → Resources → WSL Integration

2. **Permission denied errors?**
   - Add your user to docker group: `sudo usermod -aG docker $USER`
   - Log out and back in

3. **Port conflicts?**
   - Check if something is using port 616: `netstat -ano | grep 616`
   - Change the port in `docker-compose.yml`

4. **Still having issues?**
   - Check Docker logs: `docker-compose logs`
   - Restart Docker: `sudo service docker restart` (if using Option 2)
