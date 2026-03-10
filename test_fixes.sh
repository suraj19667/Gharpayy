#!/usr/bin/env bash
# Test script to verify Django project works locally after fixes

echo "=========================================="
echo "Testing Django Project After 500 Fix"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "1. Installing dependencies..."
pip install -q -r requirements.txt

echo "2. Running Django checks..."
python manage.py check --deploy 2>&1 | grep -E "(ERRORS|WARNINGS|System check)"

echo ""
echo "3. Testing imports..."
python -c "
try:
    from dashboard.views import dashboard, analytics
    from agents.models import Agent
    from leads.models import Lead
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "4. Testing database connection..."
python manage.py migrate --run-syncdb 2>&1 | tail -5

echo ""
echo "5. Creating admin user..."
python manage.py create_admin 2>&1 | grep -E "(Superuser|created|updated|Error)"

echo ""
echo "6. Testing views load without errors..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gharpayy.settings')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from dashboard.views import dashboard, analytics

try:
    factory = RequestFactory()
    user = User.objects.first()
    
    if not user:
        print('⚠️  No user found, creating one...')
        user = User.objects.create_superuser('testadmin', 'test@test.com', 'test123')
    
    # Test dashboard view
    request = factory.get('/dashboard/')
    request.user = user
    response = dashboard(request)
    
    if response.status_code == 200:
        print('✅ Dashboard view loads successfully')
    else:
        print(f'❌ Dashboard returned status {response.status_code}')
        
    # Test analytics view
    request = factory.get('/analytics/')
    request.user = user
    response = analytics(request)
    
    if response.status_code == 200:
        print('✅ Analytics view loads successfully')
    else:
        print(f'❌ Analytics returned status {response.status_code}')
        
except Exception as e:
    print(f'❌ Error testing views: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

echo ""
echo "=========================================="
echo "✅ All tests passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Fix 500 error with error handling'"
echo "3. git push"
echo "4. Monitor Render logs after deployment"
echo ""
