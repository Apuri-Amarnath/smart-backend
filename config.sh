#!/bin/bash
cd
pwd
cd smart-backend/api/migrations
shopt -s extglob
rm !(__init__.py)
echo "deleted existing migrations"
cd smart-backend/backend
rm db.sqlite3
echo "deleted sqllite file"
python -m venv .venv
echo "virtual environment created"
source .venv/bin/activate

pip install -r requirements.txt

echo "installed requirements.txt"

cd smart-backend/backend

pwd

python manage.py makemigrations
python manage.py collectstatic --noinput
pythom manage.py migrate

export $(grep -v '^#' .env | xargs)
python - <<END
from django.contrib.auth import get_user_model
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
import django
django.setup()

# Get the custom user model
User = get_user_model()

# Create superuser
if not User.objects.filter(registration_number='$ADMIN_REGISTRATION_NUMBER').exists():
    user = User.objects.create_superuser('$ADMIN_REGISTRATION_NUMBER', '$ADMIN_PASS')
    print(f'Superuser {user.registration_number} created successfully.')
else:
    print('Superuser already exists.')
END