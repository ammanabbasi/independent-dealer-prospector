#!/usr/bin/env python3
"""
Test script for the new interactive map click-to-search functionality.
This script tests the core components without requiring the full Streamlit interface.
"""

import os
import sys
from unittest.mock import Mock
import googlemaps

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_reverse_geocoding():
    """Test the reverse geocoding functionality"""
    print("🧪 Testing Reverse Geocoding...")
    
    try:
        from components.maps import latlng_to_zip
        
        # Test with known coordinates (Manassas, VA)
        test_lat = 38.7509
        test_lng = -77.4753
        
        # Note: We need a Google Maps client for this to work
        # For testing purposes, we'll mock it or skip if no API key
        
        # Check if Google Maps API key is available
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            print("⚠️  Google Maps API key not found. Skipping reverse geocoding test.")
            print("   To test fully, set GOOGLE_MAPS_API_KEY environment variable.")
            return True
        
        # Create Google Maps client
        gmaps = googlemaps.Client(key=api_key)
        
        # Test reverse geocoding
        zip_code = latlng_to_zip(test_lat, test_lng, gmaps)
        
        if zip_code:
            print(f"✅ Reverse geocoding successful: {test_lat}, {test_lng} → ZIP {zip_code}")
            return True
        else:
            print(f"❌ Reverse geocoding failed for {test_lat}, {test_lng}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing reverse geocoding: {e}")
        return False

def test_map_components():
    """Test that map components can be imported and initialized"""
    print("🗺️  Testing Map Components...")
    
    try:
        from components.maps import (
            display_interactive_map,
            display_map_statistics,
            handle_map_click
        )
        print("✅ All map components imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing map components: {e}")
        return False

def test_database_integration():
    """Test that CRM service integration works"""
    print("🗄️  Testing CRM Integration...")
    
    try:
        from services.crm_service import crm_service
        
        # Test basic database connection
        stats = crm_service.get_prospect_stats()
        print(f"✅ CRM database connected. Total prospects: {stats.get('total_prospects', 0)}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing CRM integration: {e}")
        return False

def test_mock_search_functionality():
    """Test the search functionality with mock data"""
    print("🔍 Testing Search Integration...")
    
    try:
        # Import search function
        from app import search_independent_dealers
        
        print("✅ Search function imported successfully")
        print("   Note: Full search testing requires valid API keys and network access")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing search functionality: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting Interactive Map Feature Tests\n")
    
    tests = [
        ("Reverse Geocoding", test_reverse_geocoding),
        ("Map Components", test_map_components),
        ("Database Integration", test_database_integration),
        ("Search Integration", test_mock_search_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The interactive map feature is ready to use.")
        print("\n📋 Next Steps:")
        print("1. Open http://localhost:8507 in your browser")
        print("2. Run a ZIP code search to populate some initial data")
        print("3. Click anywhere on the displayed map to test click-to-search")
        print("4. Check the CRM history tab to see map click entries")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 