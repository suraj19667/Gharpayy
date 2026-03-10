# Gharpayy CRM - Render Deployment Instructions

## ✅ Files Updated

1. **render.yaml** - Render deployment configuration
2. **build.sh** - Build script for Render
3. **Procfile** - Gunicorn start command (corrected)
4. **leads/management/commands/create_admin.py** - New management command
5. **gharpayy/settings.py** - MongoDB error handling added

## 🚀 Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Fix Render deployment configuration"
git push
```

### 2. Render Environment Variables

Make sure these are set in Render Dashboard:

**Required:**
- `SECRET_KEY` - Auto-generated or set manually
- `DEBUG` - Set to `False`
- `ALLOWED_HOSTS` - Your render domain (e.g., `gharpayy-6i20.onrender.com`)
- `MONGODB_URI` - Your MongoDB connection string
- `MONGODB_DB` - `gharpayy`

**Admin Credentials (Optional - defaults shown):**
- `ADMIN_USERNAME` - `admin` (default)
- `ADMIN_EMAIL` - `admin@gharpayy.com` (default)
- `ADMIN_PASSWORD` - `admin123` (default)

### 3. Verify Build Command in Render

In Render Dashboard, check that Build Command is:
```bash
./build.sh
```

Or use the inline command from render.yaml

### 4. Start Command

Should be:
```bash
gunicorn gharpayy.wsgi:application --log-file - --bind 0.0.0.0:$PORT
```

## 🔐 Default Login Credentials

After deployment:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change these credentials after first login!

## 📝 What Changed

1. **Fixed Module Name**: Changed from `gharpayy_crm` to `gharpayy`
2. **Added Admin Creation**: New `create_admin` command runs on every deployment
3. **Better Error Handling**: MongoDB connection errors won't crash the app
4. **Automated Setup**: Build script handles all initialization

## 🔍 Troubleshooting

If login still doesn't work after deployment:

1. Check Render logs for errors
2. Go to Render Shell and run:
   ```bash
   python manage.py create_admin
   ```
3. Verify MongoDB connection in logs
4. Check ALLOWED_HOSTS includes your Render domain

## ✅ Ready to Deploy!

Push the changes and Render will automatically redeploy with the correct configuration.
