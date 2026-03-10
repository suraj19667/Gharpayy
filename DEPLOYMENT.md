# Gharpayy CRM - Render Deployment Instructions

## ✅ Files Updated

1. **render.yaml** - Added PostgreSQL database configuration
2. **requirements.txt** - Added PostgreSQL dependencies
3. **gharpayy/settings.py** - Updated to use PostgreSQL in production
4. **build.sh** - Build script for Render
5. **Procfile** - Gunicorn start command (corrected)
6. **leads/management/commands/create_admin.py** - Management command for admin creation

## 🔴 CRITICAL FIX: SQLite to PostgreSQL

**Problem:** SQLite database is ephemeral on Render - gets deleted on every deployment
**Solution:** Using PostgreSQL for persistent data storage

## 🚀 Deployment Steps

### Option A: Using render.yaml (Recommended - Automated)

1. **Push code to GitHub:**
```bash
git add .
git commit -m "Add PostgreSQL support for Render deployment"
git push
```

2. **In Render Dashboard:**
   - Go to "Blueprints" → "New Blueprint Instance"
   - Connect your GitHub repo
   - Select the `render.yaml` file
   - Render will automatically create:
     - PostgreSQL database (gharpayy-db)
     - Web service (gharpayy-crm)
     - Link them together

3. **Set Environment Variables** (only the ones marked "sync: false"):
   - `ALLOWED_HOSTS` - Your render domain (e.g., `gharpayy-crm.onrender.com`)
   - `MONGODB_URI` - Your MongoDB connection string (if using MongoDB Atlas)

### Option B: Manual Setup

1. **Create PostgreSQL Database:**
   - In Render Dashboard → "New" → "PostgreSQL"
   - Name: `gharpayy-db`
   - Plan: Free
   - Region: Oregon (or your preferred region)

2. **Create/Update Web Service:**
   - New Web Service or go to existing service
   - Build Command:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate --run-syncdb && python manage.py create_admin && python manage.py seed_data
     ```
   
   - Start Command:
     ```bash
     gunicorn gharpayy.wsgi:application --log-file - --bind 0.0.0.0:$PORT
     ```

3. **Set Environment Variables:**
   - `DATABASE_URL` - From PostgreSQL database (Internal Connection String)
   - `SECRET_KEY` - Generate a secure key
   - `DEBUG` - `False`
   - `ALLOWED_HOSTS` - Your render domain
   - `MONGODB_URI` - Your MongoDB connection string
   - `MONGODB_DB` - `gharpayy`
   - `ADMIN_USERNAME` - `admin` (optional - default)
   - `ADMIN_PASSWORD` - `admin123` (optional - default)
   - `ADMIN_EMAIL` - `admin@gharpayy.com` (optional - default)

## 🔐 Default Login Credentials

After successful deployment:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Change these credentials immediately after first login!**

## 📝 What Changed

1. **PostgreSQL Integration**: 
   - Added `psycopg2-binary` and `dj-database-url` to requirements
   - Settings now use PostgreSQL via DATABASE_URL on Render
   - SQLite still used for local development

2. **Persistent Database**: 
   - Admin user and data now persist across deployments
   - No more login issues after redeploy!

3. **Automated Setup**: 
   - `create_admin` command runs on every build
   - Ensures admin user always exists

## 🔍 Troubleshooting

### Login Still Not Working?

1. **Check Build Logs** in Render:
   - Look for "✓ Superuser created: admin" or "✓ Superuser updated: admin"
   - Verify PostgreSQL connection succeeded

2. **Verify Environment Variables:**
   - `DATABASE_URL` should be set (from PostgreSQL database)
   - `ALLOWED_HOSTS` includes your Render domain

3. **Manual Admin Creation** (if needed):
   - Go to Render Shell
   - Run: `python manage.py create_admin`

4. **Check Database Connection:**
   - In Render Shell: `python manage.py dbshell`
   - Should connect to PostgreSQL, not SQLite

### Common Issues

- **"relation does not exist"**: Run migrations again
  ```bash
  python manage.py migrate --run-syncdb
  python manage.py create_admin
  ```

- **MongoDB connection errors**: Not critical for login, but check MONGODB_URI

- **ALLOWED_HOSTS error**: Add your Render domain to ALLOWED_HOSTS env var

## ✅ Ready to Deploy!

Push the changes and use render.yaml for automatic setup, or manually configure as per Option B above.
