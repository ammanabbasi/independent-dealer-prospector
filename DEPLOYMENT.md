# 🚀 Deployment Guide - Independent Dealer Prospector CRM

## 📋 **Pre-Deployment Checklist**

✅ **Code Ready**: All files in repository  
✅ **Requirements**: `requirements.txt` with all dependencies  
✅ **Configuration**: `.streamlit/config.toml` for optimal settings  
✅ **Documentation**: README updated with deployment info  
✅ **Secrets Template**: `secrets.toml.template` for user guidance  

## 🌟 **Option 1: Streamlit Community Cloud (Recommended)**

**Free, official hosting for Streamlit apps**

### **Step 1: Prepare Your Repository**

1. **Push to GitHub** (public repository for free tier)
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

### **Step 2: Deploy on Streamlit Cloud**

1. **Visit Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your repository
   - Choose branch: `main`
   - Main file path: `app.py`
   - App URL: Choose your custom URL (e.g., `independent-dealer-prospector`)

3. **Configure Secrets**
   - In the app settings, go to "Secrets"
   - Add your API keys and CRM configuration:
   ```toml
   GOOGLE_MAPS_API_KEY = "your-actual-google-maps-api-key"
   OPENAI_API_KEY = "your-actual-openai-api-key"
   
   # CRM Database Configuration
   DATABASE_URL = "sqlite:///crm_data.db"  # For development - use PostgreSQL for production
   
   # Communication Services (Optional)
   TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
   TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
   TWILIO_PHONE_NUMBER = "your-twilio-phone-number"
   
   SENDGRID_API_KEY = "your-sendgrid-api-key"
   FROM_EMAIL = "sales@yourdomain.com"
   FROM_NAME = "Sales Team"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Your app will be live at: `https://your-app-name.streamlit.app`

### **Step 3: Update README**
Update your README.md with the actual live URL:
```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-actual-app-url.streamlit.app)
```

---

## 🔧 **Option 2: Alternative Deployment Platforms**

### **Railway** (Simple, modern platform)

1. **Prepare files**
   Create `railway.toml`:
   ```toml
   [build]
   builder = "nixpacks"

   [deploy]
   startCommand = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
   ```

2. **Deploy**
   - Connect GitHub to Railway
   - Add environment variables in Railway dashboard
   - Auto-deploys on push

### **Render** (Free tier available)

1. **Create `render.yaml`**:
   ```yaml
   services:
     - type: web
       name: independent-dealer-prospector
       runtime: python3
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
       envVars:
         - key: GOOGLE_MAPS_API_KEY
           sync: false
         - key: OPENAI_API_KEY
           sync: false
   ```

### **Heroku** (Classic platform)

1. **Create `Procfile`**:
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku config:set GOOGLE_MAPS_API_KEY="your-key"
   heroku config:set OPENAI_API_KEY="your-key"
   ```

---

## 🔑 **API Keys Setup**

### **Google Maps API**
1. **Create Project** in [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable APIs**:
   - Places API
   - Geocoding API
   - Maps JavaScript API
3. **Create Credentials** → API Key
4. **Restrict Key** (recommended):
   - Application restrictions: HTTP referrers
   - Add your domain: `https://your-app.streamlit.app/*`

### **OpenAI API**
1. **Create Account** at [OpenAI Platform](https://platform.openai.com/)
2. **Generate API Key** in API Keys section
3. **Set Usage Limits** to control costs
4. **Monitor Usage** in dashboard

### **CRM Database Setup**

**For Development (SQLite)**
- No additional setup required
- Database file created automatically
- Data persists locally

**For Production (PostgreSQL)**
1. **Create Database** on provider (e.g., Railway, Supabase, AWS RDS)
2. **Update DATABASE_URL**:
   ```
   DATABASE_URL = "postgresql://user:password@host:port/database"
   ```

### **Communication Services (Optional)**

**Twilio (Voice & SMS)**
1. **Create Account** at [Twilio](https://www.twilio.com/)
2. **Get Account SID** and **Auth Token**
3. **Purchase Phone Number**
4. **Configure Webhooks** for incoming calls/SMS

**SendGrid (Email)**
1. **Create Account** at [SendGrid](https://sendgrid.com/)
2. **Generate API Key** with Send Mail permissions
3. **Verify Sender Identity** (email address)
4. **Set up Domain Authentication** (recommended)

---

## 🛡️ **Security Best Practices**

### **API Key Security**
- ✅ **Never commit** secrets.toml to repository
- ✅ **Use environment variables** in production
- ✅ **Restrict API keys** to specific domains
- ✅ **Monitor usage** regularly
- ✅ **Set spending limits** on APIs

### **Application Security**
- ✅ **HTTPS only** (automatic with Streamlit Cloud)
- ✅ **CORS protection** enabled
- ✅ **XSRF protection** enabled
- ✅ **No sensitive data** stored client-side

---

## 📊 **Performance Optimization**

### **Caching Strategy**
- Search results cached for 1 hour
- API calls minimized with intelligent deduplication
- Session state used for UI persistence

### **Resource Management**
- Lazy loading of maps and visualizations
- Efficient API pagination
- Progress indicators for long operations

---

## 🔄 **Continuous Deployment**

### **Automatic Updates**
1. **Streamlit Cloud**: Auto-deploys on GitHub push
2. **Testing**: Test locally before pushing
3. **Monitoring**: Check app status after deployment

### **Rollback Strategy**
- Keep previous working commits tagged
- Test major changes in separate branches
- Monitor error logs post-deployment

---

## 📈 **Monitoring & Analytics**

### **App Performance**
- Streamlit Cloud provides basic analytics
- Monitor API usage in respective dashboards
- Track user engagement through session data

### **Error Handling**
- Comprehensive try-catch blocks in code
- User-friendly error messages
- Graceful degradation for API failures

---

## 🆘 **Troubleshooting**

### **Common Issues**

**App Won't Start**
- Check requirements.txt for correct versions
- Verify secrets are properly configured
- Check logs for specific error messages

**API Errors**
- Verify API keys are active and have quota
- Check API restrictions and domains
- Monitor usage limits

**Performance Issues**
- Clear cache if needed: `st.cache_data.clear()`
- Check API response times
- Optimize search parameters

### **Debug Mode**
Enable debug information by adding this to your secrets:
```toml
DEBUG_MODE = true
```

---

## 🎯 **Production Checklist**

Before going live:

- [ ] **All API keys** configured and tested
- [ ] **Error handling** implemented for all API calls
- [ ] **User guidance** clear and comprehensive
- [ ] **Performance** tested with realistic data volumes
- [ ] **Mobile responsiveness** verified
- [ ] **Security settings** properly configured
- [ ] **Documentation** complete and accurate
- [ ] **Support contacts** updated in app

---

## 📞 **Post-Deployment Support**

### **User Onboarding**
- Create demo videos
- Provide sample ZIP codes for testing
- Document common use cases

### **Maintenance**
- Regular dependency updates
- API limit monitoring
- User feedback collection
- Performance optimization

---

**🎉 Your Independent Dealer Prospector is ready for the world!**

*For additional support with deployment, create an issue in the repository.* 