#!/bin/bash
cd
cd smart-backend/backend
pwd
cd
source smart-backend/.venv/bin/activate

pwd
cd smart-backend/backend
pwd
if [ -f db.sqlite3 ]; then
    rm db.sqlite3
    echo "deleted sqlite"
else
    echo "db.sqlite.3 does not exist"
fi

pip install -r requirements.txt
pwd

python manage.py makemigrations
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py create_initial_groups

echo "groups created "

python manage.py adddepartments_for_no_dues

echo "added departments"

#!/bin/bash

# Load environment variables from .env file
load_env() {
  export $(grep -v '^#' .env | xargs)
}

# Load environment variables
load_env

# Output loaded environment variables (optional)
echo "ADMIN_REGISTRATION_NUMBER: $ADMIN_REGISTRATION_NUMBER"
echo "ADMIN_PASS: $ADMIN_PASS"



export $(grep -v '^#' .env | xargs)

echo "ADMIN_REGISTRATION_NUMBER: $ADMIN_REGISTRATION_NUMBER"
echo "ADMIN_PASS: $ADMIN_PASS"
# Python script to create superuser
python - <<END
from django.contrib.auth import get_user_model
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
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
python manage.py runserver 0.0.0.0:$PORT
