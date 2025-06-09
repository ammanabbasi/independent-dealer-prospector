"""
Basic tests for CRM functionality
"""

import pytest
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_creation():
    """Test that database models can be created"""
    try:
        from models.database import get_db_manager
        db_manager = get_db_manager()
        db_manager.create_tables()
        assert True, "Database tables created successfully"
    except Exception as e:
        pytest.fail(f"Database creation failed: {e}")

def test_crm_service_import():
    """Test that CRM service can be imported"""
    try:
        from services.crm_service import crm_service
        assert crm_service is not None
    except Exception as e:
        pytest.fail(f"CRM service import failed: {e}")

def test_communication_service_import():
    """Test that communication service can be imported"""
    try:
        from services.communication_service import communication_service
        assert communication_service is not None
    except Exception as e:
        pytest.fail(f"Communication service import failed: {e}")

def test_ui_components_import():
    """Test that UI components can be imported"""
    try:
        from components.crm_ui import render_enhanced_prospect_card
        assert render_enhanced_prospect_card is not None
    except Exception as e:
        pytest.fail(f"UI components import failed: {e}")

if __name__ == "__main__":
    print("Running basic CRM tests...")
    
    try:
        test_database_creation()
        print("Database creation test passed")
        
        test_crm_service_import()
        print("CRM service import test passed")
        
        test_communication_service_import()
        print("Communication service import test passed")
        
        test_ui_components_import()
        print("UI components import test passed")
        
        print("\nAll basic tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1) 