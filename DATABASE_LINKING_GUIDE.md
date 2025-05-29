# 🔗 PostgreSQL Database Linking Guide for Render

## Step-by-Step: Link Database to DATABASE_URL

### Option A: During Web Service Creation

1. **Create Web Service**
   - Go to Render Dashboard → New + → Web Service
   - Connect your GitHub repository

2. **In the Configuration Page**
   - Scroll to "Environment Variables" section
   - You'll see `DATABASE_URL` field (from your render.yaml)

3. **Link Database**
   - Next to DATABASE_URL, click the dropdown arrow
   - Select "Link to Database"
   - Choose your existing PostgreSQL database
   - ✅ Database automatically linked!

### Option B: After Service Creation

1. **Go to Web Service Dashboard**
   - Find your web service in Render
   - Click on the service name

2. **Environment Tab**
   - Click "Environment" in the left sidebar
   - Find `DATABASE_URL` in the list

3. **Edit DATABASE_URL**
   - Click the pencil/edit icon next to DATABASE_URL
   - Select "Link to Database" 
   - Choose your PostgreSQL database from dropdown
   - Click "Save Changes"

### Option C: Manual Configuration (If needed)

If automatic linking doesn't work:

1. **Get Database Connection String**
   - Go to your PostgreSQL database dashboard
   - Copy the "External Database URL"
   - Format: `postgresql://user:pass@host:port/dbname`

2. **Set DATABASE_URL Manually**
   - In Environment Variables
   - Set DATABASE_URL = your connection string
   - Save changes

## ✅ Verification

After linking, your DATABASE_URL should:
- Show as "Linked to [Your Database Name]" 
- Have a green checkmark indicating successful connection
- Automatically update if database credentials change

## 🔧 Your Application is Ready

Your `database_manager.py` will automatically:
```python
# Detects DATABASE_URL and uses PostgreSQL
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Uses PostgreSQL connection
    self.conn = psycopg2.connect(database_url)
else:
    # Falls back to SQLite for local development
    self.conn = sqlite3.connect('database.db')
```

## 🚨 Troubleshooting

**If DATABASE_URL doesn't appear:**
- Ensure your PostgreSQL database is in the same Render account
- Check that the database is running (not suspended)
- Verify render.yaml includes DATABASE_URL in envVars

**If linking fails:**
- Try refreshing the page
- Manually copy the connection string from database dashboard
- Contact Render support if persistent issues

**Ready to Deploy! 🎉**
