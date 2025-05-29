# 🎯 Independent Dealer Prospector - B2B Sales Intelligence

**Professional B2B Sales Intelligence Platform for Independent Used Car Dealerships**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url-here.streamlit.app)

## 🚀 **Live Application**

**🌐 Access the live app:** [https://your-app-url-here.streamlit.app](https://your-app-url-here.streamlit.app)

This powerful B2B sales intelligence tool helps sales professionals at SaaS platforms identify, analyze, and prospect independent used car dealerships across multiple territories.

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

### 📊 **Professional B2B Features**
- **Contact Management**: Track contacted vs. not contacted prospects
- **Sales Notes**: Individual prospect notes for decision makers, pain points, and next steps
- **Territory Statistics**: Comprehensive analytics and breakdown by ZIP code
- **Sorting & Filtering**: Advanced filtering by priority, contact status, and territory

### 🎨 **Ultra-Modern Interface**
- **Glassmorphism Design**: Professional, modern UI with gradient effects
- **Interactive Cards**: Hover effects and smooth animations
- **Responsive Layout**: Perfect on desktop, tablet, and mobile devices
- **B2B Color Scheme**: Professional purple/blue gradients

### 🔍 **Intelligent Search Algorithm**
- **Franchise Filtering**: Automatically excludes major franchise dealers
- **Multiple Search Strategies**: Text-based and radius-based searches
- **Smart Caching**: Efficient API usage with 1-hour result caching
- **Debug Information**: Transparency in search results and filtering

## 🛠️ **Technology Stack**

- **Frontend**: Streamlit with custom CSS and modern design
- **Maps Integration**: Google Maps API with Places API
- **AI Intelligence**: OpenAI GPT for sales insights
- **Data Processing**: Pandas, GeoPy for location calculations
- **Visualization**: Plotly for statistics, Folium for interactive maps

## 🚀 **Quick Start**

### **Option 1: Use the Live App (Recommended)**
Simply visit the live application: [https://your-app-url-here.streamlit.app](https://your-app-url-here.streamlit.app)

### **Option 2: Run Locally**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd used-car-dealer-finder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   Create `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_MAPS_API_KEY = "your-google-maps-api-key"
   OPENAI_API_KEY = "your-openai-api-key"
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

## 📈 **Use Cases**

### **For SaaS Sales Teams**
- **Territory Planning**: Identify all independent dealers in target markets
- **Lead Generation**: Discover high-quality prospects with scoring system
- **Competitive Intelligence**: Understand market density and opportunities
- **Sales Pipeline**: Track contact attempts and prospect status

### **For Sales Managers**
- **Team Territory Assignment**: Divide territories based on prospect data
- **Performance Tracking**: Monitor team contact rates and coverage
- **Market Analysis**: AI-powered insights for strategic planning
- **ROI Optimization**: Focus efforts on highest-scoring prospects

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