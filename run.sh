#!/bin/bash
# -----------------------------------------------
# Gharpayy CRM - Start Script
# Run this from the project root: bash run.sh
# -----------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check venv exists, create if missing
if [ ! -f "venv/bin/python" ]; then
  echo "[setup] Creating virtual environment..."
  python3 -m venv venv
fi

# 2. Install / upgrade dependencies
echo "[setup] Installing dependencies..."
venv/bin/pip install --quiet -r requirements.txt

# 3. Start MongoDB if not running (macOS with Homebrew)
if command -v brew &>/dev/null; then
  if ! brew services list | grep -q "mongodb-community.*started"; then
    echo "[setup] Starting MongoDB..."
    brew services start mongodb-community
    sleep 2
  fi
fi

# 4. Run Django migrations
echo "[setup] Running migrations..."
venv/bin/python manage.py migrate --run-syncdb 2>&1 | grep -v "^$"

# 5. Seed data if no superuser exists yet
USER_EXISTS=$(venv/bin/python -c "
import django, os
os.environ['DJANGO_SETTINGS_MODULE']='gharpayy.settings'
django.setup()
from django.contrib.auth.models import User
print(User.objects.filter(username='admin').exists())
" 2>/dev/null)

if [ "$USER_EXISTS" = "False" ]; then
  echo "[setup] Seeding sample data..."
  venv/bin/python manage.py seed_data
fi

# 6. Start server
echo ""
echo "================================================"
echo "  Gharpayy CRM is running!"
echo "  URL:      http://127.0.0.1:8000"
echo "  Login:    admin / admin123"
echo "  Press Ctrl+C to stop"
echo "================================================"
echo ""
venv/bin/python manage.py runserver 8000
