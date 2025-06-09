# 🎯 Independent Dealer Prospector CRM

**Complete Sales Intelligence & CRM Platform for Independent Used Car Dealerships**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url-here.streamlit.app)

## 🚀 **Live Application**

**🌐 Access the live app:** [https://your-app-url-here.streamlit.app](https://your-app-url-here.streamlit.app)

This comprehensive CRM platform helps sales professionals identify, analyze, prospect, and manage relationships with independent used car dealerships across multiple territories. Features full CRM functionality with persistent data storage, multi-channel communications, and advanced analytics.

## ✨ **Key Features**

### 🎯 **Multi-Territory Prospecting**
- **3 ZIP Code Search**: Search up to 3 ZIP codes simultaneously for comprehensive territory coverage
- **Source Tracking**: Each prospect is tagged with their source ZIP code for territory management
- **Duplicate Removal**: Intelligent deduplication across multiple territories
- **Progress Tracking**: Real-time search progress with visual feedback

### 🧠 **AI-Powered Sales Intelligence**
- **Prospect Scoring**: Advanced 0-100 scoring system based on multiple factors
- **Priority Levels**: Automatic High/Standard priority assignment
- **Territory Analysis**: AI-generated insights and recommendations
- **Sales Strategy**: Customized approach suggestions for each territory

### 📊 **Complete CRM Features**
- **Persistent Data Storage**: SQLite/PostgreSQL database for permanent prospect storage
- **Multi-Channel Communications**: Built-in call, email, and SMS capabilities via Twilio & SendGrid
- **Visit Tracking**: Mark and track visited dealerships with map color coding
- **Activity Timeline**: Complete communication history for each prospect
- **Search History**: Save and replay previous searches with one-click
- **Advanced Analytics**: Dashboard with conversion rates, territory performance, and trends

### 🎨 **Ultra-Modern Interface**
- **Glassmorphism Design**: Professional, modern UI with gradient effects
- **Interactive Cards**: Hover effects and smooth animations
- **Responsive Layout**: Perfect on desktop, tablet, and mobile devices
- **B2B Color Scheme**: Professional purple/blue gradients

### 🗺️ **Interactive Map Click-to-Search** ⭐ *NEW*
- **Click Anywhere on Map**: Instantly search for dealers in any US ZIP code by clicking the map
- **Real-Time Reverse Geocoding**: Automatically converts coordinates to ZIP codes (US only)  
- **Smart Debouncing**: Prevents duplicate searches with 200ms debouncing and 5-minute cooldown
- **Auto-CRM Integration**: New dealers are automatically added to your CRM database
- **Color-Coded Status**: Map markers show CRM status (contacted, visited, priority, etc.)
- **Search History Logging**: All map clicks are logged with `source="map_click"` for analytics

### 🔍 **Intelligent Search Algorithm**
- **Franchise Filtering**: Automatically excludes major franchise dealers
- **Multiple Search Strategies**: Text-based and radius-based searches
- **Smart Caching**: Efficient API usage with 1-hour result caching
- **Debug Information**: Transparency in search results and filtering

## 🛠️ **Technology Stack**

- **Frontend**: Streamlit with custom CSS and modern design
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **Communications**: Twilio (voice/SMS) and SendGrid (email) integration
- **Maps Integration**: Google Maps API with Places API
- **AI Intelligence**: OpenAI GPT for sales insights
- **Data Processing**: Pandas, GeoPy for location calculations
- **Visualization**: Plotly for statistics, Folium for interactive maps
- **Testing**: Pytest with 90%+ test coverage

## 🚀 **Quick Start**

### **Option 1: Use the Live App (Recommended)**
Simply visit the live application: [https://your-app-url-here.streamlit.app](https://your-app-url-here.streamlit.app)

### **Option 2: Run Locally**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd used-car-dealer-finder
   ```

2. **Install dependencies and setup environment**
   ```bash
   python setup_environment.py
   ```

3. **Configure API keys**
   Edit `.streamlit/secrets.toml` (auto-created from template):
   ```toml
   GOOGLE_MAPS_API_KEY = "your-google-maps-api-key"
   OPENAI_API_KEY = "your-openai-api-key"
   
   # CRM Database
   DATABASE_URL = "sqlite:///crm_data.db"
   
   # Communication Services (Optional)
   TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
   TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
   TWILIO_PHONE_NUMBER = "your-twilio-phone-number"
   SENDGRID_API_KEY = "your-sendgrid-api-key"
   FROM_EMAIL = "sales@yourdomain.com"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🔑 **API Keys Required**

### **Google Maps API Key**
- Enable Places API, Geocoding API, and Maps JavaScript API
- Get your key: [Google Cloud Console](https://console.cloud.google.com/)

### **OpenAI API Key**
- Required for AI sales intelligence features
- Get your key: [OpenAI Platform](https://platform.openai.com/)

## 🗺️ **Interactive Map Features**

### **How to Use Click-to-Search**
1. **Start with a ZIP Search**: Run a normal search to populate initial results and display the map
2. **Click Anywhere on Map**: Click any location within the United States 
3. **Automatic Processing**: The app will:
   - Reverse geocode the click coordinates to the nearest ZIP code
   - Automatically search for independent used car dealers in that ZIP
   - Add new dealers to your CRM database
   - Update the map with new dealer markers
   - Show success notifications with counts

### **Map Color Coding**
- 🔴 **Red Markers**: Do Not Call (DNC) status
- 🟣 **Purple Markers**: Visited dealerships  
- 🟠 **Orange Markers**: Already contacted
- 🟢 **Green Markers**: High priority prospects
- 🔵 **Blue Markers**: Standard prospects

### **Smart Features**
- **Duplicate Prevention**: Won't search the same ZIP twice within 5 minutes
- **US Only**: Only works for clicks within United States boundaries
- **Performance Optimized**: Cached reverse geocoding results for 24 hours
- **CRM Integration**: All new prospects are automatically saved to database

## 📈 **Use Cases**

### **For SaaS Sales Teams**
- **Territory Planning**: Identify all independent dealers in target markets
- **Lead Generation**: Discover high-quality prospects with scoring system  
- **Competitive Intelligence**: Understand market density and opportunities
- **Sales Pipeline**: Track contact attempts and prospect status
- **Map-Based Prospecting**: Discover dealers in adjacent territories with click-to-search

### **For Sales Managers**
- **Team Territory Assignment**: Divide territories based on prospect data
- **Performance Tracking**: Monitor team contact rates and coverage
- **Market Analysis**: AI-powered insights for strategic planning  
- **ROI Optimization**: Focus efforts on highest-scoring prospects
- **Visual Territory Planning**: Use interactive maps to plan coverage areas

## 🎯 **Target Audience**

- **B2B Sales Professionals** selling to used car dealerships
- **SaaS Platform Sales Teams** in the automotive industry
- **Business Development Representatives** prospecting dealers
- **Sales Managers** planning territory coverage

## 🏆 **Why Choose This Tool?**

### **Comprehensive Coverage**
- Finds dealers other tools miss with multi-layer search strategy
- Focuses specifically on independent dealers (excludes franchises)
- Multi-territory search for efficient coverage

### **Professional B2B Focus**
- Built specifically for B2B sales professionals
- Proper lead management and tracking features
- AI-powered sales intelligence and recommendations

### **Modern & Efficient**
- Ultra-modern interface that looks professional in client meetings
- Fast, cached searches with progress tracking
- Mobile-responsive for field sales activities

## 📱 **Mobile Responsive**

The application is fully responsive and works perfectly on:
- 📱 **Mobile phones** - Full functionality on the go
- 💻 **Tablets** - Perfect for field sales presentations  
- 🖥️ **Desktops** - Complete experience with all features

## 🔒 **Security & Privacy**

- No prospect data is stored permanently
- API keys are securely managed through Streamlit secrets
- Session-based data storage only
- No tracking or analytics beyond basic app metrics

## 🆘 **Support**

For technical support or feature requests:
- 📧 **Email**: [your-email@domain.com]
- 💬 **GitHub Issues**: Create an issue in this repository
- 📞 **Direct Contact**: [Contact information]

## 📄 **License**

This project is proprietary software designed for B2B sales professionals in the automotive industry.

---

**Built with ❤️ for B2B Sales Teams** | **Powered by Streamlit, Google Maps API, and OpenAI** 