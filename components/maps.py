"""
Interactive Maps Component for Independent Dealer Prospector
Handles map click-to-search workflow with reverse geocoding and auto-search.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import googlemaps
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
import logging

from services.crm_service import crm_service

logger = logging.getLogger(__name__)

@st.cache_data(ttl=86400)  # Cache for 1 day
def latlng_to_zip(lat: float, lng: float, _gmaps_client) -> Optional[str]:
    """
    Reverse geocode lat/lng coordinates to nearest ZIP code (US only).
    Cached for 24 hours to improve performance.
    """
    try:
        # Perform reverse geocoding
        reverse_geocode_result = _gmaps_client.reverse_geocode((lat, lng))
        
        if not reverse_geocode_result:
            return None
        
        # Look for postal code in address components
        for result in reverse_geocode_result:
            # Check if this is a US result
            country_found = False
            postal_code = None
            
            for component in result.get('address_components', []):
                types = component.get('types', [])
                
                if 'country' in types:
                    if component.get('short_name') == 'US':
                        country_found = True
                    else:
                        break  # Not US, skip this result
                
                if 'postal_code' in types:
                    postal_code = component.get('short_name')
            
            # Return first US postal code found
            if country_found and postal_code:
                return postal_code
        
        return None
        
    except Exception as e:
        logger.error(f"Error in reverse geocoding: {e}")
        return None

def handle_map_click(click_event: Dict, gmaps_client, search_function) -> Optional[Dict]:
    """
    Handle map click events by reverse geocoding and searching for dealers.
    
    Args:
        click_event: Dict with 'lat' and 'lng' keys from map click
        gmaps_client: Google Maps client instance
        search_function: Function to call for dealer search (should accept zip_code)
    
    Returns:
        Dict with search results and metadata, or None if failed
    """
    if not click_event or 'lat' not in click_event or 'lng' not in click_event:
        return None
    
    try:
        lat = click_event['lat']
        lng = click_event['lng']
        
        # Show loading state
        with st.spinner(f"🔍 Finding ZIP code for coordinates ({lat:.4f}, {lng:.4f})..."):
            zip_code = latlng_to_zip(lat, lng, gmaps_client)
        
        if not zip_code:
            st.warning("❌ Could not find a US ZIP code for this location. Please click within the United States.")
            return None
        
        # Check if we recently searched this ZIP code to avoid duplicates
        recent_searches = st.session_state.get('recent_map_searches', [])
        current_time = datetime.now()
        
        # Remove searches older than 5 minutes
        recent_searches = [
            (search_time, search_zip) for search_time, search_zip in recent_searches
            if (current_time - search_time).total_seconds() < 300
        ]
        
        # Check if we already searched this ZIP recently
        for search_time, search_zip in recent_searches:
            if search_zip == zip_code:
                st.info(f"📍 ZIP {zip_code} was recently searched. Showing existing results.")
                return {'zip_code': zip_code, 'was_recent': True}
        
        # Perform the dealer search
        with st.spinner(f"🚗 Searching for independent used car dealers in ZIP {zip_code}..."):
            start_time = time.time()
            
            # Call the existing search function
            new_dealers = search_function(zip_code)
            
            search_duration = time.time() - start_time
        
        if not new_dealers:
            st.warning(f"📍 No independent used car dealers found in ZIP {zip_code}.")
            return {'zip_code': zip_code, 'dealers': [], 'search_duration': search_duration}
        
        # Save search to history
        search_data = {
            'zip_codes': [zip_code],
            'radius_miles': 10,  # Default radius for map clicks
            'min_rating': 0.0,
            'search_terms': {'source': 'map_click', 'coordinates': {'lat': lat, 'lng': lng}},
            'total_found': len(new_dealers),
            'search_duration_seconds': search_duration,
            'ai_insights': f"Map click search at coordinates ({lat:.4f}, {lng:.4f}) in ZIP {zip_code}",
            'new_prospects': 0,  # Will be updated by CRM
            'duplicate_prospects': 0
        }
        
        # Save search to CRM
        try:
            search_record = crm_service.save_search(search_data)
            
            # Process and save dealers to CRM
            new_prospects_count = 0
            duplicate_prospects_count = 0
            
            for dealer in new_dealers:
                # Check if dealer already exists
                existing_prospect = crm_service.get_prospect_by_place_id(dealer.get('place_id'))
                
                if existing_prospect:
                    duplicate_prospects_count += 1
                    # Link to search results
                    crm_service.link_search_prospect(
                        search_record.id,
                        existing_prospect.id,
                        dealer.get('distance', 0),
                        dealer.get('prospect_score', 0),
                        is_new=False
                    )
                else:
                    # Create new prospect
                    new_prospects_count += 1
                    prospect_data = {
                        'place_id': dealer.get('place_id'),
                        'name': dealer.get('name'),
                        'address': dealer.get('address'),
                        'phone': dealer.get('phone'),
                        'website': dealer.get('website'),
                        'rating': dealer.get('rating'),
                        'total_reviews': dealer.get('user_ratings_total', 0),
                        'latitude': dealer.get('location', {}).get('lat'),
                        'longitude': dealer.get('location', {}).get('lng'),
                        'source_zip': zip_code,
                        'distance_miles': dealer.get('distance', 0),
                        'ai_score': dealer.get('prospect_score', 0),
                        'priority': 'high' if dealer.get('priority') == 'High' else 'standard',
                        'status': 'prospect'
                    }
                    
                    saved_prospect = crm_service.save_prospect(prospect_data)
                    
                    # Link to search results
                    crm_service.link_search_prospect(
                        search_record.id,
                        saved_prospect.id,
                        dealer.get('distance', 0),
                        dealer.get('prospect_score', 0),
                        is_new=True
                    )
            
            # Update search record with final counts - fix SQL error
            search_record.new_prospects = new_prospects_count
            search_record.duplicate_prospects = duplicate_prospects_count
            crm_service._get_session().commit()
            
        except Exception as e:
            logger.error(f"Error saving map click search to CRM: {e}")
            st.warning("⚠️ Search completed but there was an issue saving to CRM.")
        
        # Add to recent searches
        recent_searches.append((current_time, zip_code))
        st.session_state.recent_map_searches = recent_searches
        
        # Update session state with new results
        if 'prospects' not in st.session_state:
            st.session_state.prospects = []
        
        # Add new dealers to session (avoiding duplicates)
        existing_place_ids = {p.get('place_id') for p in st.session_state.prospects}
        new_dealers_to_add = [d for d in new_dealers if d.get('place_id') not in existing_place_ids]
        
        st.session_state.prospects.extend(new_dealers_to_add)
        
        # Set up session state for results display - compatible with manual search format
        st.session_state.last_search = {
            'zip_code': zip_code,  # Single ZIP for map click
            'zip_codes': [zip_code],  # Also add as array for compatibility 
            'total_found': len(new_dealers),
            'search_method': 'map_click',
            'coordinates': {'lat': lat, 'lng': lng}
        }
        
        # Show success message
        new_count = len(new_dealers_to_add)
        duplicate_count = len(new_dealers) - new_count
        
        if new_count > 0:
            st.success(f"✅ Found {new_count} new dealers in ZIP {zip_code}!")
        
        if duplicate_count > 0:
            st.info(f"📊 {duplicate_count} dealers were already in your CRM.")
        
        return {
            'zip_code': zip_code,
            'dealers': new_dealers,
            'new_dealers': new_dealers_to_add,
            'search_duration': search_duration,
            'coordinates': {'lat': lat, 'lng': lng},
            'new_count': new_count,
            'duplicate_count': duplicate_count
        }
        
    except Exception as e:
        logger.error(f"Error handling map click: {e}")
        st.error(f"❌ Error processing map click: {str(e)}")
        return None

def create_interactive_dealer_map(dealers: List[Dict], center_location: Dict, gmaps_client, search_function) -> folium.Map:
    """
    Create an enhanced interactive folium map with dealers and click-to-search functionality.
    """
    # Determine appropriate zoom level based on data
    if dealers:
        # If we have dealers, zoom closer to show the area
        zoom_start = 11
    else:
        # If no dealers, zoom out to show larger area for exploration
        zoom_start = 6
    
    # Create map with enhanced styling
    m = folium.Map(
        location=[center_location['lat'], center_location['lng']],
        zoom_start=zoom_start,
        tiles='OpenStreetMap',
        control_scale=True,
        prefer_canvas=True
    )
    
    # Add custom CSS for better appearance
    m.get_root().html.add_child(folium.Element("""
    <style>
        .leaflet-container {
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .leaflet-control-zoom {
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .leaflet-control-zoom a {
            border-radius: 6px;
        }
        .folium-map {
            border-radius: 15px;
        }
    </style>
    """))
    
    # Add a feature group for dealers
    dealer_group = folium.FeatureGroup(name="Dealers")
    
    # Add dealer markers with enhanced styling
    for dealer in dealers:
        location = dealer.get('location', {})
        if location.get('lat') and location.get('lng'):
            lat, lng = location['lat'], location['lng']
            
            # Enhanced marker styling based on priority
            priority = dealer.get('priority', 'Standard')
            score = dealer.get('prospect_score', 0)
            
            if priority == 'High' or score > 80:
                marker_color = 'red'
                icon = 'star'
            elif score > 60:
                marker_color = 'orange' 
                icon = 'certificate'
            else:
                marker_color = 'green'
                icon = 'car'
            
            # Create enhanced popup with more information
            popup_content = f"""
            <div style="min-width: 250px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{dealer.get('name', 'Unknown')}</h4>
                <div style="margin-bottom: 8px;">
                    <strong>📍 Address:</strong><br>{dealer.get('address', 'N/A')}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>📞 Phone:</strong> {dealer.get('phone', 'N/A')}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>⭐ Rating:</strong> {dealer.get('rating', 0):.1f}/5.0 
                    ({dealer.get('user_ratings_total', 0)} reviews)
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>🤖 AI Score:</strong> {score}/100
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>🎯 Priority:</strong> {priority}
                </div>
                <div style="margin-bottom: 8px;">
                    <strong>📏 Distance:</strong> {dealer.get('distance', 0):.1f} miles
                </div>
            </div>
            """
            
            # Add marker with enhanced styling
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=dealer.get('name', 'Dealer'),
                icon=folium.Icon(
                    color=marker_color,
                    icon=icon,
                    prefix='fa'
                )
            ).add_to(dealer_group)
    
    # Add dealer group to map
    dealer_group.add_to(m)
    
    # Add click instructions as a control
    instructions_html = """
    <div style="position: fixed; 
                top: 80px; right: 10px; width: 300px; height: 90px;
                background-color: rgba(255, 255, 255, 0.95); 
                border: 2px solid #4facfe;
                border-radius: 10px;
                z-index: 9999; 
                font-size: 12px;
                padding: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h5 style="margin: 0 0 5px 0; color: #4facfe;">🗺️ Interactive Search</h5>
        <p style="margin: 0; color: #333; line-height: 1.3;">
            Click anywhere on the map to search for independent used car dealers in that area!
        </p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(instructions_html))
    
    # Add layer control if we have multiple layers
    if dealers:
        folium.LayerControl().add_to(m)
    
    return m

def display_interactive_map(dealers: List[Dict], center_location: Dict, gmaps_client, search_function):
    """
    Display an interactive folium map with click-to-search functionality.
    Enhanced with larger size and better visual appeal.
    """
    try:
        # Create the interactive map with enhanced styling
        interactive_map = create_interactive_dealer_map(dealers, center_location, gmaps_client, search_function)
        
        # Display the map with enhanced size and styling - MUCH LARGER
        map_data = st_folium(
            interactive_map, 
            center=center_location,
            zoom=10,
            width="100%",
            height=1000,  # Increased to 1000px to fill the entire space
            returned_objects=["last_clicked"],
            feature_group_to_add=None,
            key="interactive_dealer_map"
        )
        
        # Handle map clicks for search
        if map_data["last_clicked"] and map_data["last_clicked"]["lat"] and map_data["last_clicked"]["lng"]:
            click_event = {
                'lat': map_data["last_clicked"]["lat"],
                'lng': map_data["last_clicked"]["lng"]
            }
            
            # Process the map click
            with st.spinner("🔍 Processing map click..."):
                try:
                    result = handle_map_click(click_event, gmaps_client, search_function)
                    if result and not result.get('was_recent', False):
                        st.rerun()  # Refresh to show new results
                except Exception as e:
                    logger.error(f"Error handling map click: {e}")
                    st.error("Error processing map click. Please try again.")
                    
    except Exception as e:
        st.error(f"Error displaying map: {e}")
        logger.error(f"Map display error: {e}")

def get_map_statistics(dealers: List[Dict]) -> Dict:
    """
    Get statistics about dealers on the map for display.
    
    Args:
        dealers: List of dealer dictionaries
    
    Returns:
        Dict with map statistics
    """
    if not dealers:
        return {}
    
    stats = {
        'total_dealers': len(dealers),
        'high_priority': len([d for d in dealers if d.get('priority') == 'High']),
        'with_phone': len([d for d in dealers if d.get('phone')]),
        'with_website': len([d for d in dealers if d.get('website')]),
        'avg_score': sum(d.get('prospect_score', 0) for d in dealers) / len(dealers),
        'avg_rating': sum(d.get('rating', 0) for d in dealers if d.get('rating')) / len([d for d in dealers if d.get('rating')]) if any(d.get('rating') for d in dealers) else 0
    }
    
    # ZIP code breakdown
    zip_codes = {}
    for dealer in dealers:
        zip_code = dealer.get('source_zip', 'Unknown')
        if zip_code not in zip_codes:
            zip_codes[zip_code] = 0
        zip_codes[zip_code] += 1
    
    stats['zip_breakdown'] = zip_codes
    
    return stats

def display_map_statistics(dealers: List[Dict]):
    """
    Display map statistics in a nice format.
    
    Args:
        dealers: List of dealer dictionaries
    """
    stats = get_map_statistics(dealers)
    
    if not stats:
        return
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Dealers", stats['total_dealers'])
    
    with col2:
        st.metric("High Priority", stats['high_priority'])
    
    with col3:
        st.metric("Avg AI Score", f"{stats['avg_score']:.1f}/100")
    
    with col4:
        st.metric("Avg Rating", f"{stats['avg_rating']:.1f}⭐")
    
    # ZIP code breakdown if multiple ZIPs
    if len(stats['zip_breakdown']) > 1:
        st.markdown("#### 📍 ZIP Code Breakdown")
        
        zip_cols = st.columns(min(len(stats['zip_breakdown']), 5))
        
        for i, (zip_code, count) in enumerate(stats['zip_breakdown'].items()):
            if i < len(zip_cols):
                with zip_cols[i]:
                    st.metric(f"ZIP {zip_code}", count) 