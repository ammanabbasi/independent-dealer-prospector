# Standard library imports first
from datetime import datetime, timedelta
import time
import math
from typing import List, Dict, Optional, Tuple

# Third-party imports (non-Streamlit)
import googlemaps
import pandas as pd
import folium
from dotenv import load_dotenv
import openai
from geopy.distance import geodesic

# Streamlit imports
import streamlit as st
from streamlit_folium import st_folium

# Set page config FIRST - before any other Streamlit commands or imports that use Streamlit
st.set_page_config(
    page_title="Independent Dealer Prospector",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables for services (initialized in main)
crm_service = None
gmaps_client = None
openai_client = None

def init_session_state():
    """Initialize session state variables"""
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

def apply_css_styling():
    """Apply enhanced CSS styling"""
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

def search_independent_dealers(zip_code: str, radius_miles: int = None) -> List[Dict]:
    """Efficient search for ALL used car dealers in ZIP code, excluding only franchises."""
    
    cache_key = f"{zip_code}_efficient_all_dealers"
    if cache_key in st.session_state.search_cache:
        cache_time, cached_results = st.session_state.search_cache[cache_key]
        if datetime.now() - cache_time < timedelta(hours=1):
            return cached_results
    
    try:
        # Get location for the ZIP code
        geocode_result = gmaps_client.geocode(zip_code)
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
                result = gmaps_client.places(query=query)
                if result.get('results'):
                    for place in result['results']:
                        if place['place_id'] not in all_dealers:
                            all_dealers[place['place_id']] = place
                            debug_info["text_search"] += 1
                
                # Check for next page token
                while result.get('next_page_token'):
                    time.sleep(2)  # Required delay for pagination
                    result = gmaps_client.places(query=query, page_token=result['next_page_token'])
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
            radius_result = gmaps_client.places_nearby(
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
                radius_result = gmaps_client.places_nearby(
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
        
        # Comprehensive franchise brand list for filtering
        franchise_brands = {
            # Major automotive brands
            'toyota', 'honda', 'ford', 'chevrolet', 'chevy', 'nissan', 'mazda', 
            'hyundai', 'kia', 'subaru', 'volkswagen', 'vw', 'bmw', 'mercedes-benz', 
            'mercedes', 'audi', 'lexus', 'infiniti', 'acura', 'cadillac', 'lincoln',
            'buick', 'gmc', 'chrysler', 'dodge', 'jeep', 'ram', 'fiat', 'mitsubishi',
            'volvo', 'jaguar', 'land rover', 'porsche', 'mini', 'tesla', 'genesis',
            'alfa romeo', 'maserati', 'bentley', 'rolls-royce', 'ferrari', 'lamborghini',
            'peugeot', 'citroen', 'renault', 'seat', 'skoda', 'smart', 'saab', 'hummer',
            'saturn', 'pontiac', 'oldsmobile', 'plymouth', 'mercury', 'scion', 'isuzu',
            'suzuki', 'daewoo', 'maybach', 'mclaren', 'aston martin', 'lotus',
            # Commercial/truck brands
            'freightliner', 'peterbilt', 'kenworth', 'mack', 'international', 'volvo trucks',
            'western star', 'sterling', 'autocar', 'hino', 'isuzu commercial'
        }
        
        # Franchise indicator words/phrases
        franchise_indicators = {
            'dealership', 'dealer', 'motors', 'automotive', 'auto group', 'car country',
            'family of dealerships', 'auto mall', 'auto center', 'motor company'
        }
        
        for place_id, basic_info in all_dealers.items():
            try:
                # Get detailed information
                details = gmaps_client.place(
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
                
                # Enhanced franchise detection
                name_lower = name.lower()
                
                # Check if it's a franchise dealership
                is_franchise = False
                
                # Method 1: Direct brand match anywhere in name
                for brand in franchise_brands:
                    if brand in name_lower:
                        is_franchise = True
                        debug_info["franchise"] += 1
                        break
                
                # Method 2: Check for franchise indicator patterns
                if not is_franchise:
                    for brand in franchise_brands:
                        for indicator in franchise_indicators:
                            # Look for patterns like "Toyota Dealership", "Honda Motors", etc.
                            if brand in name_lower and indicator in name_lower:
                                is_franchise = True
                                debug_info["franchise"] += 1
                                break
                        if is_franchise:
                            break
                
                # Method 3: Check for obvious franchise patterns
                if not is_franchise:
                    franchise_patterns = [
                        'certified pre-owned', 'pre-owned certified', 'certified used',
                        'new & used', 'new and used', 'sales & service', 'sales and service',
                        'service center', 'parts & service', 'collision center'
                    ]
                    
                    # Only mark as franchise if it has BOTH a brand name AND franchise pattern
                    has_brand = any(brand in name_lower for brand in franchise_brands)
                    has_pattern = any(pattern in name_lower for pattern in franchise_patterns)
                    
                    if has_brand and has_pattern:
                        is_franchise = True
                        debug_info["franchise"] += 1
                
                # Skip franchises
                if is_franchise:
                    continue
                
                # Skip obvious non-dealers and other businesses
                skip_keywords = [
                    'rental', 'rent-a-car', 'enterprise', 'hertz', 'avis', 'budget',
                    'parts only', 'junkyard', 'salvage', 'towing', 'tow', 'wrecker',
                    'car wash', 'detail', 'detailing', 'repair only', 'mechanic only',
                    'body shop', 'collision', 'glass', 'windshield', 'tire', 'tires',
                    'oil change', 'lube', 'transmission', 'brake', 'muffler', 'exhaust',
                    'inspection', 'smog', 'emissions', 'insurance', 'financing only',
                    'parts', 'accessories', 'aftermarket', 'customization', 'tuning',
                    'racing', 'performance', 'restoration', 'classic car restoration',
                    'motorcycle', 'truck rental', 'van rental', 'trailer',
                    'parking', 'storage', 'valet', 'gas station', 'fuel', 'charging',
                    'driving school', 'dmv', 'registration', 'title', 'notary'
                ]
                
                if any(keyword in name_lower for keyword in skip_keywords):
                    debug_info["filtered_out"] += 1
                    continue
                
                # Positive filtering: Look for independent dealer indicators
                independent_indicators = [
                    'used cars', 'used car', 'pre-owned', 'auto sales', 'car sales',
                    'independent', 'family owned', 'locally owned', 'wholesale',
                    'car lot', 'auto lot', 'car mart', 'auto mart', 'car world',
                    'auto world', 'car connection', 'auto connection', 'car plaza',
                    'auto plaza', 'car emporium', 'auto emporium', 'quality used',
                    'affordable cars', 'discount auto', 'budget cars', 'economy auto',
                    'pre owned', 'previously owned', 'certified auto', 'select auto',
                    'premier auto', 'elite auto', 'choice auto', 'best buy auto',
                    'car gallery', 'auto gallery', 'car depot', 'auto depot'
                ]
                
                # Boost scoring for clear independent dealers
                has_independent_indicator = any(indicator in name_lower for indicator in independent_indicators)
                
                # If no clear independent indicators, be more cautious with generic names
                if not has_independent_indicator:
                    # Check if it's just a generic "automotive" or "motors" without clear used car focus
                    generic_only = any(word in name_lower for word in ['automotive', 'motors', 'auto']) and \
                                  not any(word in name_lower for word in ['used', 'pre-owned', 'sales', 'lot'])
                    
                    if generic_only:
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
                
                # Removed minimum rating filter as requested
                rating = details.get('rating', 0)
                
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
                
                # Bonus for independent dealer indicators
                if has_independent_indicator:
                    prospect_score += 15
                
                # Extra bonus for very clear independent indicators
                strong_independent_words = ['independent', 'family owned', 'locally owned', 'used cars', 'used car lot']
                if any(word in name_lower for word in strong_independent_words):
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
        
        st.info(f"🔍 Search Results: Text search: {debug_info['text_search']}, Radius search: {debug_info['radius_search']}, Franchises filtered: {debug_info['franchise']}, Other exclusions: {debug_info['filtered_out']}")
        
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
    
    # Add dealer markers with CRM status colors
    for idx, dealer in enumerate(dealers):
        # Get CRM prospect if available
        db_prospect = None
        if hasattr(dealer, 'place_id'):
            db_prospect = crm_service.get_prospect_by_place_id(dealer.place_id)
        elif dealer.get('place_id'):
            db_prospect = crm_service.get_prospect_by_place_id(dealer['place_id'])
        
        # Color based on CRM status
        if db_prospect:
            if db_prospect.status == 'dnc':
                color = 'red'  # Do Not Call
            elif db_prospect.is_visited:
                color = 'purple'  # Visited
            elif db_prospect.status == 'contacted':
                color = 'orange'  # Contacted
            elif db_prospect.priority == 'high':
                color = 'green'  # High priority prospect
            else:
                color = 'blue'  # Standard prospect
        else:
            # Fallback to priority-based coloring
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
    """Main application function"""
    
    # Import database module first (should be safe)
    from models.database import get_db_manager
    
    # Set global variables without instantiating CRMService yet
    global crm_service, gmaps_client, openai_client
    
    # Initialize session state first
    init_session_state()
    
    # Define cached initialization functions INSIDE main to avoid module-level execution
    @st.cache_resource
    def init_clients():
        """Initialize API clients with caching"""
        try:
            gmaps = googlemaps.Client(key=st.secrets["GOOGLE_MAPS_API_KEY"])
            openai_client = openai.Client(api_key=st.secrets["OPENAI_API_KEY"])
            return gmaps, openai_client
        except Exception as e:
            st.error("Error loading API keys. Please check your secrets.toml configuration.")
            st.stop()

    @st.cache_resource
    def init_crm():
        """Initialize CRM database and services"""
        try:
            db_manager = get_db_manager()
            db_manager.create_tables()
            return True
        except Exception as e:
            st.error(f"Error initializing CRM database: {e}")
            return False
    
    # Initialize API clients
    gmaps_client, openai_client = init_clients()
    
    # Initialize CRM database
    crm_initialized = init_crm()
    
    # Apply CSS styling
    apply_css_styling()
    
    # NOW import CRMService and components (after all other Streamlit commands)
    from services.crm_service import CRMService
    from components.crm_ui import (
        render_enhanced_prospect_card, 
        render_search_history_tab, 
        render_analytics_dashboard,
        render_batch_messaging,
        render_prospects_table
    )
    from components.maps import (
        display_interactive_map,
        display_map_statistics
    )
    
    # Now create the CRMService instance
    crm_service = CRMService()
    
    # Check CRM initialization
    if not crm_initialized:
        st.error("❌ Failed to initialize CRM database. Please check configuration.")
        return
    
    # Main app header
    st.title("🚗 Independent Dealer Prospector")
    st.markdown("*Powered by AI-Enhanced Territory Management & CRM*")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Search & Prospect", 
        "📊 Analytics", 
        "📞 Search History",
        "👥 All Prospects",
        "📧 Batch Messaging"
    ])
    
    with tab1:
        search_and_prospect_tab()
    
    with tab2:
        render_analytics_dashboard()
    
    with tab3:
        render_search_history_tab()
    
    with tab4:
        all_prospects_tab()
    
    with tab5:
        render_batch_messaging()

def search_and_prospect_tab():
    """Search and prospecting functionality with CRM integration."""
    
    # Check for replay search
    if 'replay_search' in st.session_state:
        replay_data = st.session_state.replay_search
        st.info(f"🔄 Replay search loaded: {replay_data['zip_codes']} (Radius: {replay_data['radius_miles']} miles)")
        if st.button("🗑️ Clear Replay", type="secondary"):
            del st.session_state.replay_search
            st.rerun()
    
    # Modern territory management container
    st.markdown('<div class="territory-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="territory-header">🗺️ Territory Management</h2>', unsafe_allow_html=True)
    
    # Search method selection
    st.markdown("""
        <div class="search-method-container">
            <h3 style="margin: 0 0 1rem 0; color: #333; text-align: center;">🔍 Choose Your Search Method</h3>
            <p style="margin: 0; color: #666; text-align: center;">Select how you'd like to discover independent used car dealers</p>
        </div>
    """, unsafe_allow_html=True)
    
    search_method = st.radio(
        "",
        ["🗺️ Click on Map", "📍 Enter ZIP Codes", "🔄 Both Methods"],
        horizontal=True,
        help="Click on map for instant geographic search, enter ZIP codes for precise targeting, or use both!"
    )
    
    # Interactive Map for Click-to-Search (always visible)
    if search_method in ["🗺️ Click on Map", "🔄 Both Methods"]:
        st.markdown("""
            <div class="map-container">
                <div class="map-instructions">
                    <h4>💡 Interactive Search Map</h4>
                    <p>Click anywhere in the United States to instantly find independent used car dealers in that area!</p>
                </div>
        """, unsafe_allow_html=True)
        
        # Create a default map centered on the US
        default_center = {'lat': 39.8283, 'lng': -98.5795}  # Geographic center of US
        
        # If we have existing prospects, use them for the map, otherwise create empty map
        map_prospects = st.session_state.get('prospects', [])
        if map_prospects:
            # Calculate center from existing prospects
            all_lats = [p.get('location', {}).get('lat') for p in map_prospects if p.get('location', {}).get('lat')]
            all_lngs = [p.get('location', {}).get('lng') for p in map_prospects if p.get('location', {}).get('lng')]
            
            if all_lats and all_lngs:
                default_center = {
                    'lat': sum(all_lats) / len(all_lats),
                    'lng': sum(all_lngs) / len(all_lngs)
                }
        
                        # Display the interactive map with larger height
                with st.container():
                    display_interactive_map(map_prospects, default_center, gmaps_client, lambda zip_code: search_independent_dealers(zip_code, gmaps_client))
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close map container
        
        # Add spacing
        st.markdown("---")
    
    # ZIP Code input section (conditional)
    if search_method in ["📍 Enter ZIP Codes", "🔄 Both Methods"]:
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
        
        # Enhanced search parameters with improved franchise filtering
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🗑️ Clear Cache", help="Clear search cache to use latest filtering rules"):
                if hasattr(st.session_state, 'search_cache'):
                    st.session_state.search_cache.clear()
                st.success("Cache cleared!")
        
        # Ultra-modern search button with gradient (only show if ZIP codes method is selected)
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
                    prospects = search_independent_dealers(zip_code, gmaps_client)
                    
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
                    'total_found': len(unique_prospects)
                }
                
                # Clear progress indicators
                search_progress.empty()
                status_container.empty()
                
                # Save search and prospects to CRM database
                try:
                    # Create search record
                    search_data = {
                        'zip_codes': zip_codes,
                        'radius_miles': 25,  # Default radius
                        'min_rating': 0.0,  # Set to 0 since we removed the filter
                        'total_found': len(unique_prospects),
                        'new_prospects': 0,
                        'duplicate_prospects': len(all_prospects) - len(unique_prospects),
                        'search_duration_seconds': 0,  # Could track this
                    }
                    
                    search_record = crm_service.save_search(search_data)
                    
                    # Prepare prospect data for database
                    prospects_to_save = []
                    new_count = 0
                    
                    for prospect in unique_prospects:
                        prospect_data = {
                            'place_id': prospect['place_id'],
                            'name': prospect['name'],
                            'address': prospect['address'],
                            'phone': prospect.get('phone'),
                            'website': prospect.get('website'),
                            'rating': prospect.get('rating'),
                            'total_reviews': prospect.get('user_ratings_total'),
                            'latitude': prospect.get('location', {}).get('lat'),
                            'longitude': prospect.get('location', {}).get('lng'),
                            'ai_score': prospect.get('prospect_score', 0),
                            'priority': 'high' if prospect.get('priority') == 'High' else 'standard',
                            'source_zip': prospect.get('source_zip'),
                            'distance_miles': prospect.get('distance')
                        }
                        
                        # Check if prospect already exists
                        existing = crm_service.get_prospect_by_place_id(prospect['place_id'])
                        if not existing:
                            new_count += 1
                        
                        prospects_to_save.append(prospect_data)
                    
                    # Bulk save prospects
                    saved_prospects = crm_service.bulk_save_prospects(prospects_to_save)
                    
                    # Link prospects to search
                    for i, saved_prospect in enumerate(saved_prospects):
                        original_prospect = unique_prospects[i]
                        is_new = not crm_service.get_prospect_by_place_id(saved_prospect.place_id)
                        
                        crm_service.link_search_prospect(
                            search_record.id,
                            saved_prospect.id,
                            original_prospect.get('distance', 0),
                            original_prospect.get('prospect_score', 0),
                            is_new
                        )
                    
                    # Update search record with actual new count
                    search_data['new_prospects'] = new_count
                    crm_service.save_search(search_data)
                    
                    st.info(f"💾 Saved {len(saved_prospects)} prospects to CRM ({new_count} new, {len(saved_prospects) - new_count} updated)")
                    
                except Exception as e:
                    st.warning(f"Error saving to CRM: {e}")
                    
                # Success message
                st.success(f"✅ Found {len(unique_prospects)} used car dealers across {total_zip_codes} territories!")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close territory container
    
    # Display results if available
    if st.session_state.prospects:
        prospects = st.session_state.prospects
        last_search = st.session_state.last_search
        
        # Modern results header with territory summary - handle both map click and manual search formats
        if 'zip_codes' in last_search:
            zip_code_list = ", ".join(last_search['zip_codes'])
            territory_text = f"Territories: {zip_code_list}"
        elif 'zip_code' in last_search:
            # Single ZIP from map click
            zip_code_list = last_search['zip_code']
            territory_text = f"Map Click: ZIP {zip_code_list}"
        else:
            territory_text = "Unknown search method"
            
        st.markdown(f"""
            <div class="results-header">
                🎯 {len(prospects)} Used Car Dealers Found
                <br><small>{territory_text}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Enhanced territory statistics
        contacted_count = len([p for p in prospects if p.get('contacted', False)])
        high_priority_count = len([p for p in prospects if p.get('priority') == 'High'])
        avg_score = sum(p.get('prospect_score', 0) for p in prospects) / len(prospects)
        contactable_count = len([p for p in prospects if p.get('phone')])
        
        # Statistics by ZIP code - handle both manual search and map click formats
        zip_stats = {}
        zip_codes_to_process = []
        
        if 'zip_codes' in last_search:
            zip_codes_to_process = last_search['zip_codes']
        elif 'zip_code' in last_search:
            zip_codes_to_process = [last_search['zip_code']]
            
        for zip_code in zip_codes_to_process:
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
        if len(zip_codes_to_process) > 1:
            st.markdown("### 🗺️ Territory Breakdown")
            
            breakdown_cols = st.columns(len(zip_codes_to_process))
            
            for i, zip_code in enumerate(zip_codes_to_process):
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
                if len(zip_codes_to_process) > 1:
                    zip_filter = st.selectbox("🗺️ Territory Filter", ["All"] + zip_codes_to_process)
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
                    intelligence = get_sales_intelligence(prospects, ", ".join(zip_codes_to_process))
                    
                    st.markdown("#### 📊 B2B Sales Intelligence for Territories: " + ", ".join(zip_codes_to_process))
                    
                    # Display the intelligence using native Streamlit markdown for better readability
                    with st.container():
                        st.markdown(f"""
                            <div class="sales-insight-content">
                                {intelligence.replace(chr(10), '<br>')}
                            </div>
                        """, unsafe_allow_html=True)
        
        # Interactive map display
        if prospects:
            # Calculate center location from all prospects
            all_lats = [p.get('location', {}).get('lat') for p in prospects if p.get('location', {}).get('lat')]
            all_lngs = [p.get('location', {}).get('lng') for p in prospects if p.get('location', {}).get('lng')]
            
            if all_lats and all_lngs:
                center_location = {
                    'lat': sum(all_lats) / len(all_lats),
                    'lng': sum(all_lngs) / len(all_lngs)
                }
                
                # Display interactive map with click-to-search
                display_interactive_map(prospects, center_location, gmaps_client, lambda zip_code: search_independent_dealers(zip_code, gmaps_client))
                
                # Display map statistics
                display_map_statistics(prospects)
        
        # Display filtered prospects using enhanced CRM cards
        if filtered_prospects:
            st.markdown(f"### 🎯 Prospects ({len(filtered_prospects)} of {len(prospects)})")
            
            # Convert to database prospects if possible
            db_prospects = []
            for prospect in filtered_prospects:
                db_prospect = crm_service.get_prospect_by_place_id(prospect['place_id'])
                if db_prospect:
                    db_prospects.append(db_prospect)
                else:
                    db_prospects.append(prospect)
            
            for prospect in db_prospects:
                render_enhanced_prospect_card(prospect, show_communications=True)
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

def all_prospects_tab():
    """Display all prospects in CRM with filtering and management."""
    st.markdown("## 👥 All Prospects")
    
    # Get all prospects from database
    all_prospects = crm_service.get_all_prospects()
    
    if not all_prospects:
        st.info("No prospects found in CRM. Run some searches to populate your prospect database!")
        return
    
    # Summary statistics
    stats = crm_service.get_prospect_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Prospects", stats['total_prospects'])
    
    with col2:
        st.metric("Contacted", stats['contacted'])
    
    with col3:
        st.metric("Visited", stats['visited'])
    
    with col4:
        st.metric("High Priority", stats['high_priority'])
    
    with col5:
        st.metric("Avg AI Score", f"{stats['avg_ai_score']:.1f}")
    
    # Filtering options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "prospect", "contacted", "qualified", "visited", "dnc"]
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Priority Filter", 
            ["All", "high", "standard", "low"]
        )
    
    with col3:
        visited_filter = st.selectbox(
            "Visited Filter",
            ["All", "Visited", "Not Visited"]
        )
    
    with col4:
        # Search by name/address
        search_query = st.text_input("Search", placeholder="Search by name or address...")
    
    # Apply filters
    filtered_prospects = all_prospects
    
    if status_filter != "All":
        filtered_prospects = [p for p in filtered_prospects if p.status == status_filter]
    
    if priority_filter != "All":
        filtered_prospects = [p for p in filtered_prospects if p.priority == priority_filter]
    
    if visited_filter == "Visited":
        filtered_prospects = [p for p in filtered_prospects if p.is_visited]
    elif visited_filter == "Not Visited":
        filtered_prospects = [p for p in filtered_prospects if not p.is_visited]
    
    if search_query:
        search_results = crm_service.search_prospects(search_query)
        filtered_prospect_ids = {p.id for p in search_results}
        filtered_prospects = [p for p in filtered_prospects if p.id in filtered_prospect_ids]
    
    st.markdown(f"### Showing {len(filtered_prospects)} of {len(all_prospects)} prospects")
    
    # Display options
    view_mode = st.radio("View Mode", ["Cards", "Table", "Map"], horizontal=True)
    
    if view_mode == "Cards":
        # Display as enhanced cards
        for prospect in filtered_prospects:
            render_enhanced_prospect_card(prospect, show_communications=True)
    
    elif view_mode == "Map":
        # Display interactive map
        if filtered_prospects:
            # Convert prospects to dict format for map display
            map_prospects = []
            for prospect in filtered_prospects:
                if prospect.latitude and prospect.longitude:
                    prospect_dict = {
                        'place_id': prospect.place_id,
                        'name': prospect.name,
                        'address': prospect.address,
                        'phone': prospect.phone,
                        'website': prospect.website,
                        'rating': prospect.rating,
                        'user_ratings_total': prospect.total_reviews,
                        'location': {'lat': prospect.latitude, 'lng': prospect.longitude},
                        'distance': prospect.distance_miles or 0,
                        'prospect_score': prospect.ai_score,
                        'priority': 'High' if prospect.priority == 'high' else 'Standard',
                        'source_zip': prospect.source_zip
                    }
                    map_prospects.append(prospect_dict)
            
            if map_prospects:
                # Calculate center location
                all_lats = [p['location']['lat'] for p in map_prospects]
                all_lngs = [p['location']['lng'] for p in map_prospects]
                
                center_location = {
                    'lat': sum(all_lats) / len(all_lats),
                    'lng': sum(all_lngs) / len(all_lngs)
                }
                
                # Display interactive map with click-to-search
                display_interactive_map(map_prospects, center_location, gmaps_client, lambda zip_code: search_independent_dealers(zip_code, gmaps_client))
                
                # Display map statistics
                display_map_statistics(map_prospects)
            else:
                st.info("No prospects have location data available for map display.")
        else:
            st.info("No prospects to display on map.")
    
    else:
        # Display as interactive table
        render_prospects_table(filtered_prospects, show_actions=True)

if __name__ == "__main__":
    main() 