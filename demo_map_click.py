"""
Demo script for testing the interactive map click-to-search functionality.
This script demonstrates the new features added to the Independent Dealer Prospector.
"""

import streamlit as st
from components.maps import latlng_to_zip, handle_map_click
from app import search_independent_dealers, init_clients

def demo_reverse_geocoding():
    """Demo the reverse geocoding functionality"""
    st.markdown("## 🧪 Demo: Reverse Geocoding")
    
    # Get API clients
    gmaps, _ = init_clients()
    
    # Example coordinates
    examples = [
        {"name": "Manassas, VA", "lat": 38.7509, "lng": -77.4753},
        {"name": "Arlington, VA", "lat": 38.8816, "lng": -77.0910},
        {"name": "Fairfax, VA", "lat": 38.8462, "lng": -77.3064},
        {"name": "Alexandria, VA", "lat": 38.8048, "lng": -77.0469}
    ]
    
    st.markdown("### Test Coordinates")
    
    for example in examples:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.write(f"**{example['name']}**")
        
        with col2:
            st.write(f"Lat: {example['lat']}, Lng: {example['lng']}")
        
        with col3:
            if st.button("Get ZIP", key=f"zip_{example['name']}"):
                with st.spinner("Getting ZIP code..."):
                    zip_code = latlng_to_zip(example['lat'], example['lng'], gmaps)
                    if zip_code:
                        st.success(f"ZIP: {zip_code}")
                    else:
                        st.error("No ZIP found")

def demo_map_click_simulation():
    """Demo the map click handling"""
    st.markdown("## 🗺️ Demo: Map Click Simulation")
    
    st.info("""
    In the actual app, when you click on the map:
    1. The coordinates are reverse geocoded to find the nearest ZIP code
    2. A search for independent used car dealers is automatically triggered
    3. Results are added to your CRM and displayed on the map
    4. The map re-centers on the new location
    """)
    
    # Simulate a map click
    col1, col2 = st.columns(2)
    
    with col1:
        lat = st.number_input("Latitude", value=38.7509, format="%.6f")
    
    with col2:
        lng = st.number_input("Longitude", value=-77.4753, format="%.6f")
    
    if st.button("🎯 Simulate Map Click", type="primary"):
        # Simulate the click event
        click_event = {"lat": lat, "lng": lng}
        
        st.markdown("### Processing Map Click...")
        
        # Get API clients
        gmaps, _ = init_clients()
        
        # Process the click
        result = handle_map_click(click_event, gmaps, search_independent_dealers)
        
        if result:
            st.success("Map click processed successfully!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("ZIP Code Found", result.get('zip_code', 'N/A'))
            
            with col2:
                st.metric("Dealers Found", len(result.get('dealers', [])))
            
            with col3:
                st.metric("Search Duration", f"{result.get('search_duration', 0):.1f}s")
            
            if result.get('dealers'):
                st.markdown("### 🚗 Sample Dealers Found")
                for i, dealer in enumerate(result['dealers'][:3]):  # Show first 3
                    with st.expander(f"{dealer['name']} - Score: {dealer.get('prospect_score', 0)}/100"):
                        st.write(f"**Address:** {dealer['address']}")
                        st.write(f"**Phone:** {dealer.get('phone', 'N/A')}")
                        st.write(f"**Rating:** {dealer.get('rating', 'N/A')}⭐")
                        st.write(f"**Distance:** {dealer['distance']} miles")
        else:
            st.error("Failed to process map click")

def main():
    """Main demo application"""
    st.set_page_config(
        page_title="Map Click Demo",
        page_icon="🗺️",
        layout="wide"
    )
    
    st.title("🗺️ Interactive Map Click-to-Search Demo")
    
    st.markdown("""
    This demo showcases the new **interactive map click-to-search** functionality 
    added to the Independent Dealer Prospector CRM.
    
    ## ✨ New Features:
    
    1. **🎯 Click Anywhere on Map** - Click any location in the US to instantly search that ZIP code
    2. **🔄 Reverse Geocoding** - Automatically converts coordinates to ZIP codes (US only)
    3. **📊 Real-time Results** - New dealers are added to your CRM and displayed immediately
    4. **🗺️ Map Updates** - Map re-centers and shows new dealer markers with status colors
    5. **📝 Search History** - All map clicks are logged with source="map_click"
    6. **⚡ Smart Caching** - Prevents duplicate searches in the same area
    
    ## 🎨 Color-Coded Markers:
    
    - 🔴 **Red**: Do Not Call
    - 🟣 **Purple**: Visited
    - 🟠 **Orange**: Contacted  
    - 🟢 **Green**: High Priority
    - 🔵 **Blue**: Standard Prospect
    """)
    
    # Create tabs for different demos
    tab1, tab2 = st.tabs(["🔍 Reverse Geocoding Test", "🗺️ Map Click Simulation"])
    
    with tab1:
        demo_reverse_geocoding()
    
    with tab2:
        demo_map_click_simulation()
    
    st.markdown("---")
    st.markdown("""
    ## 🚀 How to Use in the Main App:
    
    1. Go to the **"🔍 Search & Prospect"** tab
    2. Run a search for any ZIP code to get initial results
    3. Look for the interactive map below the results
    4. **Click anywhere on the map** to search that location
    5. Watch as new dealers are automatically added to your results!
    
    You can also use the map in the **"👥 All Prospects"** tab by selecting "Map" view mode.
    """)

if __name__ == "__main__":
    main() 