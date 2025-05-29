import streamlit as st
import googlemaps
import openai
import folium
from streamlit_folium import st_folium
import pandas as pd
from typing import List, Dict, Optional, Tuple
import requests
from datetime import datetime, timedelta
import time
import json
from geopy.distance import geodesic
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import re

# Set page config
st.set_page_config(
    page_title="Independent Dealer Prospector",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'prospects' not in st.session_state:
    st.session_state.prospects = []
if 'contacted' not in st.session_state:
    st.session_state.contacted = []
if 'search_cache' not in st.session_state:
    st.session_state.search_cache = {}
if 'last_search' not in st.session_state:
    st.session_state.last_search = {}
if 'sales_notes' not in st.session_state:
    st.session_state.sales_notes = {}

# Configure API clients
@st.cache_resource
def init_clients():
    try:
        gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_API_KEY"])
        openai_client = openai.Client(api_key=st.secrets["OPENAI_API_KEY"])
        return gmaps, openai_client
    except Exception as e:
        st.error("Error loading API keys. Please check your secrets.toml configuration.")
        st.stop()

gmaps, openai_client = init_clients()

# Enhanced CSS with ultra-modern, clean design
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main > div {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Ultra-modern header with glassmorphism effect */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 2;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 2;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Modern territory container with card design */
    .territory-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.04);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.8);
        position: relative;
        overflow: hidden;
    }
    
    .territory-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .territory-header {
        color: #2d3748;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    /* Enhanced ZIP code input styling */
    .zip-input-container {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .zip-input-container:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    .zip-input-label {
        color: #4a5568;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    /* Modern results header with animated gradient */
    .results-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .results-header::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%); }
        100% { transform: translateX(100%) translateY(100%); }
    }
    
    /* Ultra-modern prospect cards */
    .prospect-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .prospect-card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15), 0 8px 20px rgba(0, 0, 0, 0.08);
        border-color: #667eea;
    }
    
    .prospect-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 24px 24px 0 0;
    }
    
    .prospect-card.contacted::before {
        background: linear-gradient(90deg, #48bb78, #38a169);
    }
    
    .prospect-card.high-priority::before {
        background: linear-gradient(90deg, #f56565, #e53e3e);
    }
    
    /* Modern dealer name styling */
    .dealer-name {
        color: #2d3748;
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 1.5rem 0;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    
    /* Enhanced prospect score with modern badge */
    .prospect-score {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        letter-spacing: 0.5px;
    }
    
    /* Modern contact info grid */
    .contact-info {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .info-item {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 16px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .info-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border-left-color: #764ba2;
    }
    
    .info-icon {
        font-size: 1.5rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 2px;
        flex-shrink: 0;
    }
    
    .info-content {
        flex: 1;
    }
    
    .info-label {
        font-weight: 700;
        color: #4a5568;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    
    .info-value {
        color: #2d3748;
        font-size: 1.1rem;
        line-height: 1.5;
        font-weight: 500;
    }
    
    /* Ultra-modern status badges */
    .status-badge {
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .status-independent {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }
    
    .status-contacted {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
    }
    
    /* Enhanced territory statistics */
    .territory-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 2rem;
        margin: 2.5rem 0;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
    }
    
    .stats-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .stats-number {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
        letter-spacing: -1px;
    }
    
    .stats-label {
        color: #6c757d;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Modern sales insight section */
    .sales-insight {
        background: linear-gradient(135deg, #f8fafb 0%, #e2e8f0 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin: 2rem 0;
        position: relative;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }
    
    .sales-insight::before {
        content: '🧠';
        position: absolute;
        top: -15px;
        left: 25px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
        padding: 15px;
        border-radius: 50%;
        font-size: 1.8rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border: 2px solid #e2e8f0;
    }
    
    .sales-insight-content {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #e8ecef;
        margin-top: 1rem;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #2d3748;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Modern empty state */
    .empty-state {
        text-align: center;
        padding: 5rem 3rem;
        background: linear-gradient(135deg, #f8fafb 0%, #e2e8f0 100%);
        border-radius: 24px;
        margin: 3rem 0;
        border: 2px dashed #cbd5e0;
    }
    
    .empty-state-icon {
        font-size: 5rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .empty-state-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
    }
    
    .empty-state-text {
        color: #6c757d;
        font-size: 1.1rem;
        line-height: 1.7;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Enhanced responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .contact-info {
            grid-template-columns: 1fr;
        }
        
        .territory-stats {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .prospect-card {
            padding: 2rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in miles."""
    return geodesic((lat1, lon1), (lat2, lon2)).miles

def is_business_open(hours: List[str]) -> Tuple[bool, str]:
    """Check if business is currently open based on hours."""
    if not hours:
        return False, "Hours not available"
    
    try:
        now = datetime.now()
        weekday = now.strftime('%A')
        
        for hour_text in hours:
            if weekday in hour_text:
                if "Closed" in hour_text:
                    return False, "Closed today"
                # Simple check - could be enhanced for actual time parsing
                return True, hour_text
        
        return False, "Hours not available"
    except (ValueError, AttributeError, TypeError) as e:
        return False, "Hours not available"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def search_independent_dealers(zip_code: str, radius_miles: int = None, min_rating: float = 0.0) -> List[Dict]:
    """Efficient search for ALL used car dealers in ZIP code, excluding only franchises."""
    
    cache_key = f"{zip_code}_efficient_all_dealers"
    if cache_key in st.session_state.search_cache:
        cache_time, cached_results = st.session_state.search_cache[cache_key]
        if datetime.now() - cache_time < timedelta(hours=1):
            return cached_results
    
    try:
        # Get location for the ZIP code
        geocode_result = gmaps.geocode(zip_code)
        if not geocode_result:
            st.error(f"Could not find location for ZIP code {zip_code}")
            return []
        
        location = geocode_result[0]['geometry']['location']
        
        all_dealers = {}
        
        # Simplified search queries - focus on efficiency
        search_queries = [
            f"used car dealer {zip_code}",
            f"car dealer {zip_code}",
            f"auto dealer {zip_code}",
            f"used cars {zip_code}",
            f"auto sales {zip_code}"
        ]
        
        # Also search by type in the area
        st.info(f"🔍 Searching for all used car dealers in {zip_code}...")
        
        # Debug counter
        debug_info = {"text_search": 0, "radius_search": 0, "filtered_out": 0, "franchise": 0}
        
        # 1. Text-based searches with ZIP code
        for query in search_queries:
            try:
                result = gmaps.places(query=query)
                if result.get('results'):
                    for place in result['results']:
                        if place['place_id'] not in all_dealers:
                            all_dealers[place['place_id']] = place
                            debug_info["text_search"] += 1
                
                # Check for next page token
                while result.get('next_page_token'):
                    time.sleep(2)  # Required delay for pagination
                    result = gmaps.places(query=query, page_token=result['next_page_token'])
                    if result.get('results'):
                        for place in result['results']:
                            if place['place_id'] not in all_dealers:
                                all_dealers[place['place_id']] = place
                                debug_info["text_search"] += 1
                
            except Exception as e:
                st.warning(f"Error in text search: {str(e)}")
                continue
        
        # 2. Radius-based search around ZIP code
        try:
            # Search for car dealers within the area
            radius_result = gmaps.places_nearby(
                location=(location['lat'], location['lng']),
                radius=16000,  # ~10 miles
                type='car_dealer'
            )
            
            if radius_result.get('results'):
                for place in radius_result['results']:
                    if place['place_id'] not in all_dealers:
                        all_dealers[place['place_id']] = place
                        debug_info["radius_search"] += 1
            
            # Handle pagination
            while radius_result.get('next_page_token'):
                time.sleep(2)
                radius_result = gmaps.places_nearby(
                    location=(location['lat'], location['lng']),
                    page_token=radius_result['next_page_token']
                )
                if radius_result.get('results'):
                    for place in radius_result['results']:
                        if place['place_id'] not in all_dealers:
                            all_dealers[place['place_id']] = place
                            debug_info["radius_search"] += 1
                            
        except Exception as e:
            st.warning(f"Error in radius search: {str(e)}")
        
        st.info(f"Found {len(all_dealers)} total businesses before filtering")
        
        # Process all found dealers
        processed_dealers = []
        
        # Define franchise brands to exclude (ONLY clear franchises)
        franchise_brands = {
            'toyota', 'honda', 'ford', 'chevrolet', 'chevy', 'nissan', 'mazda', 
            'hyundai', 'kia', 'subaru', 'volkswagen', 'vw', 'bmw', 'mercedes-benz', 
            'mercedes', 'audi', 'lexus', 'infiniti', 'acura', 'cadillac', 'lincoln',
            'buick', 'gmc', 'chrysler', 'dodge', 'jeep', 'ram', 'fiat', 'mitsubishi',
            'volvo', 'jaguar', 'land rover', 'porsche', 'mini', 'tesla', 'genesis',
            'alfa romeo', 'maserati', 'bentley', 'rolls-royce', 'ferrari', 'lamborghini'
        }
        
        for place_id, basic_info in all_dealers.items():
            try:
                # Get detailed information
                details = gmaps.place(
                    place_id,
                    fields=['name', 'formatted_address', 'formatted_phone_number', 
                           'website', 'rating', 'user_ratings_total', 'url', 
                           'geometry', 'business_status']
                )['result']
                
                # Skip if closed
                if details.get('business_status') == 'CLOSED_PERMANENTLY':
                    debug_info["filtered_out"] += 1
                    continue
                
                name = details.get('name', '').strip()
                address = details.get('formatted_address', '')
                
                # Only check if ZIP code is in address
                if zip_code not in address:
                    debug_info["filtered_out"] += 1
                    continue
                
                # Simple franchise check - ONLY exclude if it's clearly a franchise
                name_lower = name.lower()
                
                # Check if it's a franchise dealership
                is_franchise = False
                for brand in franchise_brands:
                    # Only mark as franchise if brand name is at the START of the business name
                    # This indicates it's an official franchise
                    if name_lower.startswith(brand + ' ') or name_lower == brand:
                        is_franchise = True
                        debug_info["franchise"] += 1
                        break
                
                # Skip only clear franchises
                if is_franchise:
                    continue
                
                # Skip obvious non-dealers
                skip_keywords = ['rental', 'rent-a-car', 'enterprise', 'hertz', 'avis', 
                               'budget', 'parts only', 'junkyard', 'salvage', 'towing',
                               'car wash', 'detail', 'repair only', 'mechanic only']
                
                if any(keyword in name_lower for keyword in skip_keywords):
                    debug_info["filtered_out"] += 1
                    continue
                
                # Calculate distance
                dealer_location = details.get('geometry', {}).get('location', {})
                if dealer_location:
                    distance = calculate_distance(
                        location['lat'], location['lng'],
                        dealer_location['lat'], dealer_location['lng']
                    )
                else:
                    distance = 0
                
                # Apply minimum rating filter
                rating = details.get('rating', 0)
                if rating and rating < min_rating:
                    debug_info["filtered_out"] += 1
                    continue
                
                # Simple scoring - less aggressive
                prospect_score = 50  # Base score
                
                # Rating bonus
                if rating:
                    if rating >= 4.5:
                        prospect_score += 20
                    elif rating >= 4.0:
                        prospect_score += 15
                    elif rating >= 3.5:
                        prospect_score += 10
                
                # Reviews bonus
                reviews = details.get('user_ratings_total', 0)
                if reviews >= 100:
                    prospect_score += 15
                elif reviews >= 50:
                    prospect_score += 10
                elif reviews >= 20:
                    prospect_score += 5
                
                # Has website/phone
                if details.get('website'):
                    prospect_score += 10
                if details.get('formatted_phone_number'):
                    prospect_score += 10
                
                # Create dealer record
                dealer = {
                    'place_id': place_id,
                    'name': name,
                    'address': address,
                    'phone': details.get('formatted_phone_number'),
                    'website': details.get('website'),
                    'rating': rating,
                    'user_ratings_total': reviews,
                    'maps_url': details.get('url'),
                    'location': dealer_location,
                    'distance': round(distance, 1),
                    'prospect_score': min(prospect_score, 100),
                    'priority': 'High' if prospect_score >= 70 else 'Standard'
                }
                
                processed_dealers.append(dealer)
                
            except Exception as e:
                st.warning(f"Error processing dealer: {str(e)}")
                continue
        
        # Sort by score and distance
        processed_dealers.sort(key=lambda x: (-x['prospect_score'], x['distance']))
        
        # Cache results
        st.session_state.search_cache[cache_key] = (datetime.now(), processed_dealers)
        
        st.info(f"Debug Info: Text search found {debug_info['text_search']}, Radius search found {debug_info['radius_search']}, Filtered out {debug_info['filtered_out']}, Franchises excluded {debug_info['franchise']}")
        
        st.success(f"✅ Found {len(processed_dealers)} used car dealers in {zip_code}")
        
        return processed_dealers
        
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return []

def get_sales_intelligence(prospects: List[Dict], territory: str) -> str:
    """Generate B2B sales intelligence for territory planning."""
    if not prospects:
        return "No used car dealer prospects found to analyze."
    
    # Prepare prospect summary for AI analysis
    prospect_summary = []
    high_priority_count = 0
    total_score = 0
    
    for prospect in prospects[:15]:  # Top 15 prospects
        priority_emoji = "🔥" if prospect.get('priority') == 'High' else "📍"
        if prospect.get('priority') == 'High':
            high_priority_count += 1
        
        total_score += prospect['prospect_score']
        
        summary = (f"{priority_emoji} {prospect['name']}: "
                  f"Score {prospect['prospect_score']}/100 | "
                  f"{prospect.get('rating') or 'No'}⭐ ({prospect.get('user_ratings_total', 0)} reviews) | "
                  f"{prospect['distance']} miles | "
                  f"{'Website' if prospect.get('website') else 'No Website'} | "
                  f"{'Phone Available' if prospect.get('phone') else 'No Phone'}")
        prospect_summary.append(summary)
    
    avg_score = total_score / len(prospects[:15]) if prospects else 0
    
    prompt = f"""
    Analyze this B2B sales territory for used car dealerships near {territory}:
    
    TERRITORY OVERVIEW:
    - Total Prospects: {len(prospects)}
    - High Priority Prospects: {high_priority_count}
    - Average Prospect Score: {avg_score:.1f}/100
    
    TOP PROSPECTS:
    {chr(10).join(prospect_summary)}
    
    As a B2B sales expert for a SaaS platform targeting used car dealerships, provide:
    
    1. **Territory Assessment**: Quality of this territory for dealer prospecting
    2. **Top 3 Prospects**: Which dealers to contact first and why (include specific business reasons)
    3. **Sales Strategy**: Recommended approach for this territory (phone, email, in-person visits)
    4. **Market Insights**: What this territory tells us about the local market
    5. **Objection Handling**: Likely objections from dealers and how to overcome them
    
    Focus on practical B2B sales advice for SaaS prospecting.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a B2B sales intelligence expert specializing in automotive SaaS solutions for used car dealerships. Provide actionable sales insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sales intelligence unavailable: {str(e)}"

def create_dealer_map(dealers: List[Dict], center_location: Dict) -> folium.Map:
    """Create an interactive map with dealer locations."""
    m = folium.Map(
        location=[center_location['lat'], center_location['lng']],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add center marker
    folium.Marker(
        [center_location['lat'], center_location['lng']],
        popup="Search Location",
        icon=folium.Icon(color='red', icon='home'),
        tooltip="Your Search Location"
    ).add_to(m)
    
    # Add dealer markers
    for idx, dealer in enumerate(dealers):
        # Color based on priority
        if dealer.get('priority') == 'High':
            color = 'green'
        else:
            color = 'blue'
        
        # Create popup content
        rating_text = f"{dealer.get('rating', 'N/A')}" if dealer.get('rating') else "Not rated"
        popup_html = f"""
        <div style="width: 300px;">
            <h4>{dealer['name']}</h4>
            <p><strong>Rating:</strong> {rating_text}⭐ ({dealer.get('user_ratings_total', 0)} reviews)</p>
            <p><strong>Distance:</strong> {dealer['distance']} miles</p>
            <p><strong>Address:</strong> {dealer['address']}</p>
            <p><strong>Phone:</strong> {dealer.get('phone', 'Not available')}</p>
            <p><strong>Score:</strong> {dealer.get('prospect_score', 0)}/100</p>
        </div>
        """
        
        folium.Marker(
            [dealer['location']['lat'], dealer['location']['lng']],
            popup=folium.Popup(popup_html, max_width=400),
            icon=folium.Icon(color=color, icon='car'),
            tooltip=f"{dealer['name']} - Score: {dealer.get('prospect_score', 0)}/100"
        ).add_to(m)
    
    return m

def display_prospect_card(prospect):
    """Display ultra-modern prospect card with source ZIP tracking."""
    
    # Determine priority styling
    priority_class = "high-priority" if prospect.get('priority') == 'High' else ""
    contacted_class = "contacted" if prospect.get('contacted', False) else ""
    card_classes = f"prospect-card {priority_class} {contacted_class}".strip()
    
    # Create the main card container
    st.markdown(f'<div class="{card_classes}">', unsafe_allow_html=True)
    
    # Header section with name and score
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<h2 class="dealer-name">{prospect["name"]}</h2>', unsafe_allow_html=True)
        
        # Status badges
        badge_html = '<div style="display: flex; gap: 12px; margin: 1rem 0;">'
        badge_html += '<span class="status-badge status-independent">✅ Independent</span>'
        
        if prospect.get('contacted', False):
            badge_html += '<span class="status-badge status-contacted">📞 Contacted</span>'
        
        if prospect.get('priority') == 'High':
            badge_html += '<span class="status-badge" style="background: linear-gradient(135deg, #f56565, #e53e3e); color: white;">🎯 High Priority</span>'
        
        # Source ZIP badge
        if prospect.get('source_zip'):
            badge_html += f'<span class="status-badge" style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white;">📍 {prospect["source_zip"]}</span>'
        
        badge_html += '</div>'
        st.markdown(badge_html, unsafe_allow_html=True)
    
    with col2:
        # Prospect score with modern styling
        score = prospect.get('prospect_score', 0)
        st.markdown(f"""
            <div class="prospect-score">
                🎯 {score}/100
            </div>
        """, unsafe_allow_html=True)
    
    # Contact information grid
    st.markdown('<div class="contact-info">', unsafe_allow_html=True)
    
    # Address
    address = prospect.get('address', 'Address not available')
    st.markdown(f"""
        <div class="info-item">
            <div class="info-icon">📍</div>
            <div class="info-content">
                <div class="info-label">Business Address</div>
                <div class="info-value">{address}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Phone (if available)
    if prospect.get('phone'):
        phone = prospect['phone']
        st.markdown(f"""
            <div class="info-item">
                <div class="info-icon">📞</div>
                <div class="info-content">
                    <div class="info-label">Phone Number</div>
                    <div class="info-value">{phone}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Rating and reviews
    rating = prospect.get('rating', 'Not rated')
    review_count = prospect.get('user_ratings_total', 0)
    rating_display = f"{rating:.1f} ⭐" if isinstance(rating, (int, float)) else rating
    st.markdown(f"""
        <div class="info-item">
            <div class="info-icon">⭐</div>
            <div class="info-content">
                <div class="info-label">Customer Rating</div>
                <div class="info-value">{rating_display} ({review_count} reviews)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Website (if available)
    if prospect.get('website'):
        website = prospect['website']
        st.markdown(f"""
            <div class="info-item">
                <div class="info-icon">🌐</div>
                <div class="info-content">
                    <div class="info-label">Website</div>
                    <div class="info-value">{website}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close contact-info
    
    # Sales actions
    st.markdown("---")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        # Contact status toggle
        contact_key = f"contact_{prospect['place_id']}"
        if st.button(
            "📞 Mark Contacted" if not prospect.get('contacted', False) else "✅ Contacted",
            key=contact_key,
            disabled=prospect.get('contacted', False),
            use_container_width=True
        ):
            # Update prospect status
            for i, p in enumerate(st.session_state.prospects):
                if p['place_id'] == prospect['place_id']:
                    st.session_state.prospects[i]['contacted'] = True
                    break
            st.rerun()
    
    with action_col2:
        # Priority toggle
        priority_key = f"priority_{prospect['place_id']}"
        current_priority = prospect.get('priority', 'Standard')
        new_priority = "Standard" if current_priority == "High" else "High"
        
        if st.button(
            f"🎯 {new_priority} Priority",
            key=priority_key,
            use_container_width=True
        ):
            # Update prospect priority
            for i, p in enumerate(st.session_state.prospects):
                if p['place_id'] == prospect['place_id']:
                    st.session_state.prospects[i]['priority'] = new_priority
                    break
            st.rerun()
    
    with action_col3:
        # Website link
        if prospect.get('website'):
            st.link_button(
                "🌐 Visit Website",
                prospect['website'],
                use_container_width=True
            )
        else:
            st.button(
                "🌐 No Website",
                disabled=True,
                use_container_width=True,
                key=f"no_website_{prospect['place_id']}"
            )
    
    with action_col4:
        # Google Maps directions
        if prospect.get('address'):
            # Create Google Maps directions URL
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={prospect['address'].replace(' ', '+')}"
            st.link_button(
                "🗺️ Directions",
                maps_url,
                use_container_width=True
            )
        else:
            st.button(
                "🗺️ No Address",
                disabled=True,
                use_container_width=True,
                key=f"no_address_{prospect['place_id']}"
            )
    
    # Sales notes section
    notes_key = f"notes_{prospect['place_id']}"
    current_notes = st.session_state.sales_notes.get(prospect['place_id'], "")
    
    st.markdown("### 📝 Sales Notes")
    notes = st.text_area(
        "Track decision makers, pain points, follow-ups, etc.",
        value=current_notes,
        key=notes_key,
        height=100,
        placeholder="Add notes about this prospect: decision makers, budget, pain points, next steps..."
    )
    
    # Save notes
    if notes != current_notes:
        st.session_state.sales_notes[prospect['place_id']] = notes
        st.success("📝 Notes saved!")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close prospect-card

def display_statistics(prospects: List[Dict]):
    """Display B2B sales territory statistics."""
    if not prospects:
        return
    
    # Calculate B2B sales metrics
    high_priority_count = len([p for p in prospects if p.get('priority') == 'High'])
    avg_prospect_score = sum(p['prospect_score'] for p in prospects) / len(prospects)
    contactable_prospects = len([p for p in prospects if p.get('phone')])
    
    # Create 4 columns for B2B statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(prospects)}</div>
                <div class="stats-label">Total Dealers</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{high_priority_count}</div>
                <div class="stats-label">High Priority</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{avg_prospect_score:.0f}/100</div>
                <div class="stats-label">Avg Score</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{contactable_prospects}</div>
                <div class="stats-label">Have Phone</div>
            </div>
        """, unsafe_allow_html=True)

def main():
    """Main Streamlit application with ultra-modern multi-ZIP search capability."""
    # Initialize session state
    if 'prospects' not in st.session_state:
        st.session_state.prospects = []
    if 'search_cache' not in st.session_state:
        st.session_state.search_cache = {}
    if 'last_search' not in st.session_state:
        st.session_state.last_search = {}
    
    # Ultra-modern header with glassmorphism effect
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🎯 Independent Dealer Prospector</h1>
            <p class="main-subtitle">B2B Sales Intelligence for Independent Used Car Dealerships</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Modern territory management container
    st.markdown('<div class="territory-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="territory-header">🗺️ Territory Management</h2>', unsafe_allow_html=True)
    
    # Enhanced multi-ZIP code input section
    st.markdown("""
        <div class="zip-input-container">
            <div class="zip-input-label">🎯 Target ZIP Codes (Up to 3)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for ZIP code inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        zip_code_1 = st.text_input(
            "Primary ZIP Code",
            placeholder="e.g., 20110",
            help="Enter the main ZIP code for your territory"
        )
    
    with col2:
        zip_code_2 = st.text_input(
            "Secondary ZIP Code (Optional)",
            placeholder="e.g., 20111",
            help="Add a second ZIP code to expand your search"
        )
    
    with col3:
        zip_code_3 = st.text_input(
            "Third ZIP Code (Optional)",
            placeholder="e.g., 20112",
            help="Add a third ZIP code for comprehensive coverage"
        )
    
    # Collect all valid ZIP codes
    zip_codes = []
    for zip_code in [zip_code_1, zip_code_2, zip_code_3]:
        if zip_code and zip_code.strip() and len(zip_code.strip()) == 5 and zip_code.strip().isdigit():
            zip_codes.append(zip_code.strip())
    
    # Enhanced search parameters
    min_rating = st.slider(
        "⭐ Minimum Rating",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1,
        help="Filter dealers by minimum Google rating (0.0 = show all)"
    )
    
    # Ultra-modern search button with gradient
    if st.button("🚀 Launch Multi-Territory Search", type="primary", use_container_width=True):
        if not zip_codes:
            st.error("⚠️ Please enter at least one valid 5-digit ZIP code.")
        else:
            # Search all ZIP codes
            all_prospects = []
            total_zip_codes = len(zip_codes)
            
            # Create progress tracking
            search_progress = st.progress(0)
            status_container = st.empty()
            
            for i, zip_code in enumerate(zip_codes):
                status_container.markdown(f"""
                    <div class="results-header">
                        🔍 Searching Territory {i+1}/{total_zip_codes}: {zip_code}
                        <br><small>Comprehensive search in progress...</small>
                    </div>
                """, unsafe_allow_html=True)
                
                # Search this ZIP code
                prospects = search_independent_dealers(
                    zip_code, 
                    min_rating=min_rating
                )
                
                # Add ZIP code source to each prospect
                for prospect in prospects:
                    prospect['source_zip'] = zip_code
                
                all_prospects.extend(prospects)
                
                # Update progress
                progress = (i + 1) / total_zip_codes
                search_progress.progress(progress)
                
                # Brief delay between searches
                time.sleep(0.5)
            
            # Remove duplicates based on place_id
            seen_ids = set()
            unique_prospects = []
            for prospect in all_prospects:
                if prospect['place_id'] not in seen_ids:
                    seen_ids.add(prospect['place_id'])
                    unique_prospects.append(prospect)
            
            # Store results
            st.session_state.prospects = unique_prospects
            st.session_state.last_search = {
                'zip_codes': zip_codes,
                'min_rating': min_rating,
                'total_found': len(unique_prospects)
            }
            
            # Clear progress indicators
            search_progress.empty()
            status_container.empty()
            
            # Success message
            st.success(f"✅ Found {len(unique_prospects)} used car dealers across {total_zip_codes} territories!")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close territory container
    
    # Display results if available
    if st.session_state.prospects:
        prospects = st.session_state.prospects
        last_search = st.session_state.last_search
        
        # Modern results header with territory summary
        zip_code_list = ", ".join(last_search['zip_codes'])
        st.markdown(f"""
            <div class="results-header">
                🎯 {len(prospects)} Used Car Dealers Found
                <br><small>Territories: {zip_code_list} | Min Rating: {last_search.get('min_rating', 0.0)}⭐</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Enhanced territory statistics
        contacted_count = len([p for p in prospects if p.get('contacted', False)])
        high_priority_count = len([p for p in prospects if p.get('priority') == 'High'])
        avg_score = sum(p.get('prospect_score', 0) for p in prospects) / len(prospects)
        contactable_count = len([p for p in prospects if p.get('phone')])
        
        # Statistics by ZIP code
        zip_stats = {}
        for zip_code in last_search['zip_codes']:
            zip_prospects = [p for p in prospects if p.get('source_zip') == zip_code]
            zip_stats[zip_code] = {
                'count': len(zip_prospects),
                'avg_score': sum(p.get('prospect_score', 0) for p in zip_prospects) / len(zip_prospects) if zip_prospects else 0,
                'high_priority': len([p for p in zip_prospects if p.get('priority') == 'High'])
            }
        
        # Display overall statistics
        st.markdown("### 📊 Multi-Territory Analytics")
        
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{len(prospects)}</div>
                    <div class="stats-label">Total Prospects</div>
                </div>
            """, unsafe_allow_html=True)
        
        with stat_cols[1]:
            st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{high_priority_count}</div>
                    <div class="stats-label">High Priority</div>
                </div>
            """, unsafe_allow_html=True)
        
        with stat_cols[2]:
            st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{avg_score:.1f}</div>
                    <div class="stats-label">Avg Score</div>
                </div>
            """, unsafe_allow_html=True)
        
        with stat_cols[3]:
            st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{contactable_count}</div>
                    <div class="stats-label">Contactable</div>
                </div>
            """, unsafe_allow_html=True)
        
        # ZIP code breakdown
        if len(last_search['zip_codes']) > 1:
            st.markdown("### 🗺️ Territory Breakdown")
            
            breakdown_cols = st.columns(len(last_search['zip_codes']))
            
            for i, zip_code in enumerate(last_search['zip_codes']):
                stats = zip_stats[zip_code]
                with breakdown_cols[i]:
                    st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{stats['count']}</div>
                            <div class="stats-label">{zip_code}</div>
                            <div style="font-size: 0.8rem; color: #6c757d; margin-top: 0.5rem;">
                                Avg: {stats['avg_score']:.1f} | High Priority: {stats['high_priority']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Enhanced prospect management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sorting and filtering options
            sort_options = {
                "Prospect Score (High to Low)": lambda x: -x.get('prospect_score', 0),
                "Prospect Score (Low to High)": lambda x: x.get('prospect_score', 0),
                "Rating (High to Low)": lambda x: -x.get('rating', 0),
                "Name (A-Z)": lambda x: x.get('name', '').lower(),
                "Source ZIP Code": lambda x: x.get('source_zip', '')
            }
            
            sort_by = st.selectbox("📊 Sort Prospects By", list(sort_options.keys()))
            prospects_sorted = sorted(prospects, key=sort_options[sort_by])
            
            # Filtering options
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                priority_filter = st.selectbox("🎯 Priority Filter", ["All", "High Priority", "Standard"])
            
            with filter_col2:
                contact_filter = st.selectbox("📞 Contact Status", ["All", "Contacted", "Not Contacted"])
            
            with filter_col3:
                if len(last_search['zip_codes']) > 1:
                    zip_filter = st.selectbox("🗺️ Territory Filter", ["All"] + last_search['zip_codes'])
                else:
                    zip_filter = "All"
            
            # Apply filters
            filtered_prospects = prospects_sorted
            
            if priority_filter == "High Priority":
                filtered_prospects = [p for p in filtered_prospects if p.get('priority') == 'High']
            
            if contact_filter == "Contacted":
                filtered_prospects = [p for p in filtered_prospects if p.get('contacted', False)]
            elif contact_filter == "Not Contacted":
                filtered_prospects = [p for p in filtered_prospects if not p.get('contacted', False)]
            
            if zip_filter != "All":
                filtered_prospects = [p for p in filtered_prospects if p.get('source_zip') == zip_filter]
        
        with col2:
            # AI Sales Intelligence
            if st.button("🧠 Generate Sales Intelligence", type="primary", use_container_width=True):
                with st.spinner("🤖 Analyzing multi-territory data and generating sales insights..."):
                    intelligence = get_sales_intelligence(prospects, ", ".join(last_search['zip_codes']))
                    
                    st.markdown("#### 📊 B2B Sales Intelligence for Territories: " + ", ".join(last_search['zip_codes']))
                    
                    # Display the intelligence using native Streamlit markdown for better readability
                    with st.container():
                        st.markdown(f"""
                            <div class="sales-insight-content">
                                {intelligence.replace(chr(10), '<br>')}
                            </div>
                        """, unsafe_allow_html=True)
        
        # Display filtered prospects
        if filtered_prospects:
            st.markdown(f"### 🎯 Prospects ({len(filtered_prospects)} of {len(prospects)})")
            
            for prospect in filtered_prospects:
                display_prospect_card(prospect)
        else:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <div class="empty-state-title">No prospects match your filters</div>
                    <div class="empty-state-text">Try adjusting your filter criteria to see more results.</div>
                </div>
            """, unsafe_allow_html=True)
    
    else:
        # Enhanced empty state
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🚀</div>
                <div class="empty-state-title">Ready to Launch Your Sales Mission</div>
                <div class="empty-state-text">
                    Enter up to 3 ZIP codes above to discover independent used car dealers in your target territories.
                    Our multi-layer search technology will find prospects other tools miss.
                </div>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 