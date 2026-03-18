# Internship Skill Gap Analyzer

A complete full-stack web application designed to help diploma and engineering students analyze the gap between their current skills and the skills required for industry job roles and internships.

## Project Features
- **Modern Landing Page**: Aesthetic hero section, "How it Works" layout, and responsive navigation.
- **User Authentication**: Register, Login, and Logout functionality.
- **Skill Gap Analyzer Tool**: A multi-step interactive form:
  - Step 1: Branch Selection
  - Step 2: Dynamic Skill Selection
  - Step 3: Job Role Selection
- **Results & Recommendations**: Progress bar showing skill match percentage, list of missing skills, and curated learning resources (e.g., YouTube tutorials, W3Schools/GeeksforGeeks links).
- **Admin Dashboard**: Fully configured Django admin panel to manage branches, skills, user profiles, and job roles.

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL Server installed and running.

### 1. Database Configuration
By default, the project is configured to use MySQL.
- Open MySQL command line or a GUI tool like MySQL Workbench.
- Create a new database named `skill_gap_db`:
  ```sql
  CREATE DATABASE skill_gap_db;
  ```

### 2. Create a Virtual Environment
Navigate to the project directory and create a virtual environment:
```bash
cd skill_gap_analyzer
python -m venv venv
```

Activate the virtual environment:
- **Windows**: `venv\Scripts\activate`
- **macOS/Linux**: `source venv/bin/activate`

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```
*(Note: If you encounter issues installing `mysqlclient` on Windows, you can uncomment the pymysql fallback in `config/settings.py` or install the necessary C++ build tools).*

### 4. Configure Database Credentials
Edit `config/settings.py` and modify the `DATABASES` section if your MySQL username or password differs from the defaults (`root` / empty password).

### 5. Run Migrations
Apply the initial migrations to construct the database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser
Create an admin account to access the Django admin panel and manage application data (branches, skills, job roles):
```bash
python manage.py createsuperuser
```
Follow the prompts to set your email and password.

### 7. Start the Development Server
Run the local development server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` to view the application!

## Pre-populating Data
To make the site functional, log into the admin panel at `http://127.0.0.1:8000/admin/` and add some sample Branches, Skills, Job Roles, and Required Skills.
