# Mass Tracking Application

This repository contains the source code for the Mass Tracking Application, which consists of a Django backend (API) and a React frontend.

## Local Development Setup

Follow these steps to set up and run the application on your local machine.

### Prerequisites

*   Python 3.8+
*   Node.js (LTS version) & npm
*   Git

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/willymsfs/Mass-Track-2025.git
cd Mass-Track-2025
```

### 2. Backend Setup (Django)

Navigate to the backend directory, create a virtual environment, install dependencies, and set up the database.

```bash
cd mass_tracker_backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
python manage.py makemigrations mass_tracker_core
python manage.py migrate
python manage.py createsuperuser
### 3. Frontend Setup (React)

Navigate to the frontend directory and install dependencies.

```bash
cd ../mass-tracker-frontend
npm install
```

### 4. Running the Application

#### 4.1. Start the Backend Server

In a new terminal, navigate to the `mass_tracker_backend` directory and start the Django development server:

```bash
cd mass_tracker_backend
source venv/bin/activate
python manage.py runserver
```

This will typically run on `http://127.0.0.1:8000/`.

#### 4.2. Start the Frontend Development Server

In another new terminal, navigate to the `mass-tracker-frontend` directory and start the React development server:

```bash
cd mass-tracker-frontend
npm start
```

This will typically open the application in your browser at `http://localhost:3000/`.

### 5. Accessing the Application

Open your web browser and go to `http://localhost:3000/`.

*   You can register a new priest account or use the superuser account created earlier to log in.
*   The Django Admin panel is accessible at `http://127.0.0.1:8000/admin/`.

## Project Structure

```
mass-track-app/
├── mass_tracker_backend/  # Django Backend
│   ├── mass_tracker_backend/ # Main project settings
│   ├── mass_tracker_core/    # Core application (models, views, serializers, urls)
│   ├── manage.py
│   └── venv/                 # Python Virtual Environment
├── mass-tracker-frontend/ # React Frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── node_modules/
└── README.md
```




## Cloud Deployment (Heroku Example)

This section provides instructions for deploying your Mass Tracking application to Heroku. Heroku is a platform as a service (PaaS) that allows you to deploy, run, and manage applications entirely in the cloud.

### Prerequisites

*   A Heroku account (sign up at [https://www.heroku.com/](https://www.heroku.com/))
*   Heroku CLI installed ([https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli))
*   Git installed

### 1. Prepare Backend for Heroku

#### 1.1. Install Gunicorn and dj-database-url

Navigate to your backend directory and install `gunicorn` (a Python WSGI HTTP Server for Unix) and `dj-database-url` (to parse database URLs):

```bash
cd mass_tracker_backend
source venv/bin/activate
pip install gunicorn dj-database-url psycopg2-binary
pip freeze > requirements.txt
```

#### 1.2. Create a Procfile

Create a file named `Procfile` (no extension) in the `mass_tracker_backend` directory with the following content:

```
web: gunicorn mass_tracker_backend.wsgi --log-file -
```

This tells Heroku how to run your web application.

#### 1.3. Update Django Settings

Modify `mass_tracker_backend/settings.py` to configure for Heroku. Add the following imports and settings:

```python
import os
import dj_database_url

# ... (existing settings)

# Heroku: Parse database configuration from DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'))
}

# Heroku: Allow all host headers
ALLOWED_HOSTS = ['*']

# Heroku: Use WhiteNoise for static files (install later if needed)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-insecure-default-key') # Use environment variable for production

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG_VALUE', 'True') == 'True'

```

### 2. Prepare Frontend for Heroku

For the React frontend, you can either deploy it separately as a static site (e.g., using Netlify, Vercel, or Heroku Buildpack for Create React App) or serve it from your Django backend. For simplicity, we'll assume serving it from Django for now. This requires building the React app and placing the static files in a location Django can serve.

#### 2.1. Build React App

Navigate to your frontend directory and build the production version of your React app:

```bash
cd mass-tracker-frontend
npm run build
```

This will create a `build` folder with your static files.

#### 2.2. Configure Django to Serve Frontend

Move the `build` folder into your Django `mass_tracker_backend` directory (e.g., `mass_tracker_backend/staticfiles_build`).

Update `mass_tracker_backend/settings.py` to serve static files and the React app:

```python
# ... (existing settings)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add the build directory of your React app to STATICFILES_DIRS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mass-tracker-frontend/build/static'),
]

# For serving the React app index.html
TEMPLATES = [
    {
        # ... (existing template settings)
        'DIRS': [os.path.join(BASE_DIR, 'mass-tracker-frontend/build')],
    },
]

# Add WhiteNoise for serving static files in production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add this line
    # ... (rest of your middleware)
]

# Install WhiteNoise: pip install whitenoise
```

Also, update your `mass_tracker_backend/urls.py` to serve the React app's `index.html` for all unmatched routes:

```python
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mass_tracker_core.urls')),
    re_path(r'^.*', TemplateView.as_view(template_name='index.html')),
]
```

### 3. Deploy to Heroku

#### 3.1. Login to Heroku CLI

```bash
heroku login
```

#### 3.2. Create a Heroku App

Navigate to your main project directory (`mass-track-app`) and create a new Heroku app:

```bash
cd .. # Go back to mass-track-app directory
heroku create your-app-name # Replace your-app-name with a unique name
```

#### 3.3. Add Heroku Buildpacks

```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs # If you serve frontend from Django
```

#### 3.4. Push to Heroku

```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

#### 3.5. Run Migrations on Heroku

```bash
heroku run python mass_tracker_backend/manage.py migrate
```

#### 3.6. Open the App

```bash
heroku open
```

Your application should now be live on Heroku! Remember to set `SECRET_KEY` and `DEBUG_VALUE` environment variables on Heroku for production.

```bash
heroku config:set SECRET_KEY='your_super_secret_key_here'
heroku config:set DEBUG_VALUE='False'
```





## GitHub Actions for Automated Deployment

This project includes a GitHub Actions workflow to automate the deployment of your application to Heroku whenever changes are pushed to the `main` branch.

### 1. Configure GitHub Secrets

To enable the GitHub Actions deployment, you need to set up the following secrets in your GitHub repository:

1.  Go to your repository on GitHub.
2.  Click on **Settings**.
3.  In the left sidebar, click on **Secrets and variables** > **Actions**.
4.  Click on **New repository secret** and add the following:
    *   `HEROKU_API_KEY`: Your Heroku API key. You can find this in your Heroku account settings under `Account` -> `API Key`.
    *   `HEROKU_APP_NAME`: The exact name of your Heroku application (e.g., `your-app-name`).
    *   `HEROKU_EMAIL`: The email address associated with your Heroku account.

### 2. Workflow Details

The workflow is defined in `.github/workflows/deploy.yml` and performs the following steps:

*   **Checkout code:** Clones your repository.
*   **Set up Node.js:** Installs Node.js for frontend build.
*   **Install Frontend Dependencies:** Installs `npm` packages for the React app.
*   **Build Frontend:** Creates a production build of the React app.
*   **Set up Python:** Installs Python for backend dependencies.
*   **Install Backend Dependencies:** Installs `pip` packages for the Django app.
*   **Deploy to Heroku:** Uses the `akhileshns/heroku-deploy` action to deploy the Django backend (which will also serve the built React frontend).
*   **Run Migrations on Heroku:** Executes Django database migrations on the Heroku dyno.

Once these secrets are configured, every push to the `main` branch will automatically trigger a deployment to your Heroku application.


