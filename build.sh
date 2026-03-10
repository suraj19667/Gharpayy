#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --run-syncdb
python manage.py create_admin
python manage.py seed_data

echo "✓ Build completed successfully!"
