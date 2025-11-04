# Personal Finance Management Web Application

A comprehensive web-based solution for personal finance tracking, monitoring, and analysis. This application provides users with tools to manage their expenses, investments, and financial goals while offering insights into spending patterns and trends.

## Features

- **User Authentication & Authorization**: Secure login system with role-based access control
- **Expense Tracking**: Comprehensive waste/expense management system
- **Investment Monitoring**: Track and analyze investment portfolios
- **Financial Resume**: Overview dashboard with key financial metrics
- **Data Visualization**: Interactive charts and tables for financial analysis
- **Security**: CSRF protection, session management, and encrypted connections

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 4, jQuery, DataTables
- **Authentication**: Flask-Login, Flask-Security
- **Database Migration**: Flask-Migrate with Alembic
- **Development Environment**: WSL (Windows Subsystem for Linux)

## Prerequisites

- Python 3.8+
- PostgreSQL database server
- WSL environment (recommended for development)
- pip package manager

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Finances webapp"
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 5. Database Configuration

Ensure PostgreSQL is running and create the database:
```bash
# Connect to PostgreSQL (adjust host IP for WSL)
psql -h 172.17.192.1 -U postgres

# Create database
CREATE DATABASE personalfinances;
```

### 6. Database Migration
```bash
# Initialize migration repository (if needed)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 7. Run the Application
```bash
flask run
```

The application will be available at `http://127.0.0.1:616`

## Project Structure

```
app/
├── blueprints/          # Application modules
│   ├── investments/     # Investment tracking functionality
│   ├── login/          # Authentication system
│   ├── resume/         # Financial dashboard
│   ├── valoracion/     # Evaluation algorithms
│   └── wastes/         # Expense tracking
├── static/             # Static assets (CSS, JS, images)
├── templates/          # HTML templates
├── extensions.py       # Flask extensions configuration
├── models.py          # Database models
└── __init__.py        # Application factory
```

## Configuration

The application uses environment-specific configuration through `credentials.py`. Key configurations include:

- Database connection settings
- Security keys and CSRF protection
- Flask-Security settings
- Session management

## WSL Development Notes

This application is optimized for development in WSL (Windows Subsystem for Linux). The system automatically detects WSL environment and adjusts the database connection to use the Windows host IP address.

## Database Models

- **Users**: User authentication and profile management
- **Roles**: Role-based access control
- **Financial Records**: Transaction and investment data
- **Categories**: Expense and income categorization

## Security Features

- CSRF protection on all forms
- Secure session management
- Content Security Policy (CSP) headers
- Rate limiting on endpoints
- Password hashing and secure authentication

## License

This project is for personal use and educational purposes.