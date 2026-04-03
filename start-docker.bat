@echo off
REM Finances Webapp - Quick Start Script for Windows

echo 🐳 Finances Webapp - Docker Setup
echo ==================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo ✅ Created .env file. Please edit it with your configuration.
        echo.
        set /p REPLY="Do you want to edit .env now? (y/n) "
        if /i "%REPLY%"=="y" notepad .env
    ) else (
        echo ❌ .env.example not found. Cannot create .env file.
        exit /b 1
    )
)

echo.
echo 🚀 Starting Docker containers...
echo.

REM Stop existing containers if any
docker-compose down 2>nul

REM Build and start containers
docker-compose up -d --build

echo.
echo ⏳ Waiting for database to be ready...
timeout /t 5 /nobreak >nul

REM Run database migrations
echo 📦 Running database migrations...
docker-compose exec -T web flask db upgrade

echo.
echo ✅ Setup complete!
echo.
echo 📊 Container status:
docker-compose ps
echo.
echo 🌐 Application is running at: http://localhost:616
echo.
echo 📝 Useful commands:
echo    View logs:           docker-compose logs -f
echo    Stop containers:     docker-compose down
echo    Restart:             docker-compose restart
echo    Database shell:      docker-compose exec db psql -U postgres -d personalfinances
echo.
echo 📖 For more information, see README.docker.md
echo.
pause
