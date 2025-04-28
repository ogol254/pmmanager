# ProjectManager Flask Application

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL and update the `DATABASE_URL` environment variable if needed. Default is:
   ```
   postgresql://postgres:postgres@localhost:5432/postgres
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access Swagger API docs at: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

## Project Structure

- `app.py` - Main app, configuration, error handlers
- `models.py` - Database models
- `manage.py` - Migration commands
- `requirements.txt` - Dependencies

## Features
- PostgreSQL database with SQLAlchemy
- Flask-Migrate for migrations
- Auto API documentation with Swagger (Flasgger)
- Comprehensive HTTP error handlers
