# Deployment Guide

This guide will help you deploy the **AI-Powered Attendance Management System** to production using **Netlify (Frontend)** and **Render (Backend)**.

## 📋 Prerequisites

Before you begin, make sure you have:

- A [GitHub](https://github.com) account and your project pushed to GitHub
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account (Free tier available)
- A [Render](https://render.com) account (Free tier available)
- A [Netlify](https://www.netlify.com) account (Free tier available)

## 🗄️ Step 1: Set Up MongoDB Atlas (Database)

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for a free account

2. **Create a Cluster**
   - Click "Build a Database"
   - Choose "M0 Sandbox" (Free tier)
   - Select your preferred cloud provider and region
   - Click "Create Cluster"

3. **Configure Database Access**
   - Go to "Database Access" in left sidebar
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Create username and password (save these!)
   - Set privileges to "Read and write to any database"
   - Click "Add User"

4. **Configure Network Access**
   - Go to "Network Access" in left sidebar
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" in left sidebar
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/`)
   - Replace `<password>` with your actual password
   - Add database name at the end: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/attendance_system`

## 🚀 Step 2: Deploy Backend to Render

1. **Push Your Code to GitHub**
   ```bash
   cd attendance-system
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Create Render Account**
   - Go to [Render](https://render.com)
   - Sign up with GitHub

3. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository
   - Select the repository containing your project

4. **Configure Build Settings**
   - **Name**: `attendance-system-backend` (or your preferred name)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

5. **Add Environment Variables**
   Click "Advanced" and add these environment variables:
   
   | Key | Value |
   |-----|-------|
   | `MONGODB_URI` | Your MongoDB Atlas connection string from Step 1 |
   | `FLASK_ENV` | `production` |
   | `PYTHON_VERSION` | `3.11.0` |

6. **Create Disk for Uploads** (Important!)
   - Scroll to "Disks" section
   - Click "Add Disk"
   - **Name**: `uploads-disk`
   - **Mount Path**: `/opt/render/project/src/uploads`
   - **Size**: 1 GB
   - Click "Save"

7. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)
   - Copy your backend URL (e.g., `https://attendance-system-backend.onrender.com`)

## 🌐 Step 3: Deploy Frontend to Netlify

1. **Create Production Environment File**
   
   In the `frontend` folder, create a `.env.production` file:
   ```bash
   REACT_APP_API_URL=https://your-backend-url.onrender.com
   ```
   Replace `your-backend-url.onrender.com` with your actual Render backend URL from Step 2.

2. **Update Netlify Configuration**
   
   Edit `frontend/netlify.toml` and update the `REACT_APP_API_URL`:
   ```toml
   [build.environment]
     NODE_VERSION = "18.17.0"
     REACT_APP_API_URL = "https://your-backend-url.onrender.com"
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add production environment configuration"
   git push origin main
   ```

4. **Create Netlify Account**
   - Go to [Netlify](https://www.netlify.com)
   - Sign up with GitHub

5. **Create New Site**
   - Click "Add new site" → "Import an existing project"
   - Choose "Deploy with GitHub"
   - Authorize Netlify
   - Select your repository

6. **Configure Build Settings**
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
   - Click "Show advanced" → "New variable"
   
   Add environment variable:
   | Key | Value |
   |-----|-------|
   | `REACT_APP_API_URL` | Your Render backend URL |

7. **Deploy**
   - Click "Deploy site"
   - Wait for deployment (2-5 minutes)
   - Your site will be live at a Netlify URL (e.g., `https://random-name-123.netlify.app`)

8. **Optional: Custom Domain**
   - Go to "Domain settings"
   - Add your custom domain
   - Follow DNS configuration instructions

## ✅ Step 4: Verify Deployment

1. **Test Backend**
   - Open your Render backend URL in browser
   - Add `/api/health` to the URL
   - You should see: `{"status": "healthy", "timestamp": "..."}`

2. **Test Frontend**
   - Open your Netlify URL
   - Try navigating through different sections
   - Test image upload and attendance processing

3. **Test Full System**
   - Create a course
   - Add a student with photo
   - Upload a class photo
   - Verify attendance is recorded

## 🔧 Important Configuration Notes

### Backend (Render)

- **Free Tier Limitations**:
  - Service spins down after 15 minutes of inactivity
  - First request after inactivity takes 50+ seconds (cold start)
  - 750 hours/month free (enough for one service)

- **CORS Configuration**: Already configured in `app.py` with `CORS(app)`

- **File Uploads**: Persistent disk is required for storing student photos and uploaded images

### Frontend (Netlify)

- **Environment Variables**: Must start with `REACT_APP_` to be accessible in React
- **Redirects**: Configured in `netlify.toml` for React Router
- **Build**: Automatically rebuilds on every push to main branch

## 🐛 Troubleshooting

### Backend Issues

**Problem**: 502 Bad Gateway on Render
- **Solution**: Check Render logs, verify MongoDB connection string is correct

**Problem**: Module not found errors
- **Solution**: Ensure all dependencies are in `requirements.txt`

**Problem**: Database connection timeout
- **Solution**: Verify MongoDB Network Access allows all IPs (0.0.0.0/0)

### Frontend Issues

**Problem**: API requests fail with CORS errors
- **Solution**: Verify CORS is enabled in backend `app.py`

**Problem**: API URL is still localhost
- **Solution**: Check `REACT_APP_API_URL` in Netlify environment variables

**Problem**: 404 on page refresh
- **Solution**: Verify `netlify.toml` has correct redirect rules

## 📊 Monitoring

### Backend Monitoring (Render)
- View logs: Render Dashboard → Your Service → Logs
- Monitor metrics: Check CPU/Memory usage in dashboard

### Frontend Monitoring (Netlify)
- View deployments: Netlify Dashboard → Deploys
- Analytics: Available in Netlify dashboard

## 🔄 Updating Your Application

### Update Backend
```bash
# Make changes to backend code
cd backend
git add .
git commit -m "Update backend"
git push origin main
# Render automatically redeploys
```

### Update Frontend
```bash
# Make changes to frontend code
cd frontend
git add .
git commit -m "Update frontend"
git push origin main
# Netlify automatically rebuilds and redeploys
```

## 💰 Cost Considerations

### Free Tier Limits

**MongoDB Atlas (Free M0)**:
- 512 MB storage
- Shared CPU
- Sufficient for testing and small deployments

**Render (Free Tier)**:
- 750 hours/month
- 512 MB RAM
- Service sleeps after 15 min inactivity
- Free SSL

**Netlify (Free Tier)**:
- 100 GB bandwidth/month
- Unlimited sites
- Automatic SSL
- Form submissions: 100/month

### When to Upgrade

Consider paid plans when:
- Your app needs 24/7 availability without cold starts (Render: $7/month)
- You exceed free tier bandwidth (Netlify: $19/month)
- You need more database storage (MongoDB: $9/month for M10)

## 🎉 You're Live!

Your attendance system is now deployed and accessible worldwide! 

- **Frontend**: `https://your-site-name.netlify.app`
- **Backend**: `https://your-backend-name.onrender.com`

Share the frontend URL with your users to start taking attendance with face recognition!

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Netlify Documentation](https://docs.netlify.com)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

## ⚠️ Security Recommendations

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Rotate MongoDB credentials** regularly
3. **Enable MongoDB Atlas alerts** for unusual activity
4. **Monitor Render logs** for errors and suspicious activity
5. **Use strong passwords** for database users
6. **Keep dependencies updated** - Run `pip list --outdated` and `npm outdated` regularly

---

Need help? Check the troubleshooting section or create an issue on GitHub!
