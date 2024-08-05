#!/bin/bash

# Ensure the script is being run from the correct directory
cd "$(dirname "$0")"

# Optional: Remove old SQLite database if it exists
if [ -f db.sqlite3 ]; then
    rm db.sqlite3
    echo "Deleted old SQLite database."
else
    echo "No existing SQLite database found."
fi

# Apply migrations and collect static files
python manage.py makemigrations
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser if not exists
python - <<END
from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

User = get_user_model()
admin_reg_number = os.getenv('ADMIN_REGISTRATION_NUMBER')
admin_pass = os.getenv('ADMIN_PASS')

if not User.objects.filter(registration_number=admin_reg_number).exists():
    user = User.objects.create_superuser(admin_reg_number, admin_pass)
    print(f'Superuser {user.registration_number} created successfully.')
else:
    print('Superuser already exists.')
END
