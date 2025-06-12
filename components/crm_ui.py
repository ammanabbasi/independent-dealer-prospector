"""
CRM UI Components for Independent Dealer Prospector
Enhanced UI components with communication panels, visited tracking, and history.
"""

# Standard library imports
from datetime import datetime

# Third-party imports
import streamlit as st
import pandas as pd
from typing import List
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

# Import services dynamically to avoid circular imports

def _get_prospect_value(prospect, key, default=None):
    """Helper function to safely get values from prospect (dict or SQLAlchemy object)"""
    if hasattr(prospect, key):
        value = getattr(prospect, key)
        return value if value is not None else default
    elif isinstance(prospect, dict):
        return prospect.get(key, default)
    else:
        return default

def render_communication_panel(prospect_id: int, prospect_data, crm_service=None, communication_service=None):
    """Render communication panel for a prospect"""
    
    st.markdown("### 📞 Communications")
    
    # Get prospect contact info
    phone = _get_prospect_value(prospect_data, 'phone', '')
    email = _get_prospect_value(prospect_data, 'contact_email', '')
    name = _get_prospect_value(prospect_data, 'name', 'Dealership')
    place_id = _get_prospect_value(prospect_data, 'place_id', 'unknown')
    
    # Generate unique widget counter for this panel
    if 'widget_counter' not in st.session_state:
        st.session_state.widget_counter = 0
    st.session_state.widget_counter += 1
    panel_counter = st.session_state.widget_counter
    
    # Communication buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Call", key=f"call_{prospect_id}_{place_id}_{panel_counter}", use_container_width=True):
            if phone:
                show_call_modal(prospect_id, phone, name, crm_service, communication_service)
            else:
                st.error("No phone number available")
    
    with col2:
        if st.button("📧 Email", key=f"email_{prospect_id}_{place_id}_{panel_counter}", use_container_width=True):
            if email:
                show_email_modal(prospect_id, email, name, crm_service, communication_service)
            else:
                st.error("No email address available")
    
    with col3:
        if st.button("💬 SMS", key=f"sms_{prospect_id}_{place_id}_{panel_counter}", use_container_width=True):
            if phone:
                show_sms_modal(prospect_id, phone, name, crm_service, communication_service)
            else:
                st.error("No phone number available")
    
    # Communication history
    if communication_service:
        communications = communication_service.get_prospect_communications(prospect_id)
    else:
        communications = []
    
    if communications:
        st.markdown("#### Recent Communications")
        for comm in communications[:5]:  # Show last 5
            with st.expander(f"{comm['channel'].upper()} - {comm['created_at'].strftime('%m/%d %H:%M')}"):
                st.write(f"**Status:** {comm['status']}")
                if comm['subject']:
                    st.write(f"**Subject:** {comm['subject']}")
                if comm['message']:
                    st.write(f"**Message:** {comm['message']}")
                if comm['response']:
                    st.write(f"**Response:** {comm['response']}")

def show_call_modal(prospect_id: int, phone: str, name: str, crm_service=None, communication_service=None):
    """Show call initiation modal"""
    # Generate unique keys for this modal
    if 'widget_counter' not in st.session_state:
        st.session_state.widget_counter = 0
    st.session_state.widget_counter += 1
    modal_counter = st.session_state.widget_counter
    
    with st.container():
        st.markdown("#### 📞 Make Call")
        st.write(f"**Calling:** {name}")
        st.write(f"**Number:** {phone}")
        
        # Call options
        message = st.text_area(
            "Call Script (optional)",
            placeholder="Enter a custom message for the call...",
            key=f"call_message_{prospect_id}_{modal_counter}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 Initiate Call", use_container_width=True, key=f"initiate_call_{prospect_id}_{modal_counter}"):
                if communication_service:
                    result = communication_service.make_call(prospect_id, phone, message)
                else:
                    result = {'success': False, 'error': 'Communication service not available'}
                if result['success']:
                    st.success(f"Call initiated! SID: {result['call_sid']}")
                else:
                    st.error(f"Call failed: {result['error']}")
        
        with col2:
            if st.button("📝 Log Manual Call", use_container_width=True, key=f"log_call_{prospect_id}_{modal_counter}"):
                # Log a manual call record
                comm_data = {
                    'channel': 'call',
                    'direction': 'outbound',
                    'status': 'manual_log',
                    'message': message or f"Manual call log for {name}"
                }
                if crm_service:
                    crm_service.log_communication(prospect_id, comm_data)
                    st.success("Call logged manually")
                else:
                    st.error('CRM service not available')

def show_email_modal(prospect_id: int, email: str, name: str, crm_service=None, communication_service=None):
    """Show email composition modal"""
    # Generate unique keys for this modal
    if 'widget_counter' not in st.session_state:
        st.session_state.widget_counter = 0
    st.session_state.widget_counter += 1
    modal_counter = st.session_state.widget_counter
    
    with st.container():
        st.markdown("#### 📧 Send Email")
        st.write(f"**To:** {email}")
        
        # Email templates
        templates = communication_service.get_email_templates() if communication_service else [] if communication_service else []
        template_names = [t['name'] for t in templates]
        
        selected_template = st.selectbox(
            "Email Template",
            ["Custom"] + template_names,
            key=f"email_template_{prospect_id}_{modal_counter}"
        )
        
        if selected_template != "Custom":
            template = next(t for t in templates if t['name'] == selected_template)
            subject = template['subject'].replace('{{dealership_name}}', name)
            content = f"Dear {name} team,\n\n[Template content would be loaded here]\n\nBest regards,\nSales Team"
        else:
            subject = f"Automotive Solutions for {name}"
            content = ""
        
        subject = st.text_input("Subject", value=subject, key=f"email_subject_{prospect_id}_{modal_counter}")
        content = st.text_area("Email Content", value=content, height=200, key=f"email_content_{prospect_id}_{modal_counter}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📧 Send Email", use_container_width=True, key=f"send_email_{prospect_id}_{modal_counter}"):
                if subject and content:
                    if communication_service:
                        if communication_service:
                result = communication_service.send_email(
                            prospect_id, email, subject, content
                        )
                    else:
                        result = {'success': False, 'error': 'Communication service not available'}
                    if result['success']:
                        st.success("Email sent successfully!")
                    else:
                        st.error(f"Email failed: {result['error']}")
                else:
                    st.error("Please enter subject and content")
        
        with col2:
            if st.button("📝 Save Draft", use_container_width=True, key=f"save_draft_{prospect_id}_{modal_counter}"):
                # Save as draft (could implement later)
                st.info("Draft functionality coming soon")

def show_sms_modal(prospect_id: int, phone: str, name: str, crm_service=None, communication_service=None):
    """Show SMS composition modal"""
    # Generate unique keys for this modal
    if 'widget_counter' not in st.session_state:
        st.session_state.widget_counter = 0
    st.session_state.widget_counter += 1
    modal_counter = st.session_state.widget_counter
    
    with st.container():
        st.markdown("#### 💬 Send SMS")
        st.write(f"**To:** {phone}")
        
        # SMS templates
        templates = communication_service.get_sms_templates() if communication_service else [] if communication_service else []
        template_names = [t['name'] for t in templates]
        
        selected_template = st.selectbox(
            "SMS Template",
            ["Custom"] + template_names,
            key=f"sms_template_{prospect_id}_{modal_counter}"
        )
        
        if selected_template != "Custom":
            template = next(t for t in templates if t['name'] == selected_template)
            message = template['message'].replace('{{contact_name}}', name)
        else:
            message = ""
        
        message = st.text_area(
            "Message (160 chars max)",
            value=message,
            max_chars=160,
            height=100,
            key=f"sms_message_{prospect_id}_{modal_counter}"
        )
        
        char_count = len(message)
        st.caption(f"Characters: {char_count}/160")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Send SMS", use_container_width=True, key=f"send_sms_{prospect_id}_{modal_counter}"):
                if message:
                    if communication_service:
                        result = communication_service.send_sms(prospect_id, phone, message)
                    else:
                        result = {'success': False, 'error': 'Communication service not available'}
                    if result['success']:
                        st.success("SMS sent successfully!")
                    else:
                        st.error(f"SMS failed: {result['error']}")
                else:
                    st.error("Please enter a message")
        
        with col2:
            if st.button("📝 Log Manual SMS", use_container_width=True, key=f"log_sms_{prospect_id}_{modal_counter}"):
                comm_data = {
                    'channel': 'sms',
                    'direction': 'outbound',
                    'status': 'manual_log',
                    'message': message
                }
                if crm_service:
                    crm_service.log_communication(prospect_id, comm_data)
                    st.success("SMS logged manually")
                else:
                    st.error('CRM service not available')

def render_enhanced_prospect_card(prospect, show_communications=True, crm_service=None, communication_service=None, show_checkbox=False):
    """Render enhanced prospect card with CRM features"""
    
    # Get database prospect if we have an ID
    db_prospect = None
    if hasattr(prospect, 'id'):
        db_prospect = prospect
    else:
        place_id = _get_prospect_value(prospect, 'place_id')
        if place_id:
            db_prospect = crm_service.get_prospect_by_place_id(place_id) if crm_service else None
    
    # Status colors
    status_colors = {
        'prospect': '#3498db',
        'contacted': '#f39c12', 
        'qualified': '#2ecc71',
        'visited': '#9b59b6',
        'dnc': '#e74c3c'
    }
    
    status = db_prospect.status if db_prospect else 'prospect'
    visited = db_prospect.is_visited if db_prospect else False
    
    # Card styling
    card_color = status_colors.get(status, '#3498db')
    border_style = "3px solid" if visited else "1px solid"
    
    with st.container():
        st.markdown(f"""
        <div style="
            border: {border_style} {card_color};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            background: {'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)' if visited else 'white'};
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        ">
        """, unsafe_allow_html=True)
        
        # Header with status and visited indicators
        if show_checkbox:
            col1, col2, col3, col4 = st.columns([0.5, 2.5, 1, 1])
        else:
            col1, col2, col3 = st.columns([3, 1, 1])
        
        # Checkbox column (only when show_checkbox=True)
        if show_checkbox:
            with col1:
                place_id = _get_prospect_value(prospect, 'place_id')
                if place_id:
                    if 'selected_dealers' not in st.session_state:
                        st.session_state.selected_dealers = []
                    
                    # Create unique checkbox key
                    if 'widget_counter' not in st.session_state:
                        st.session_state.widget_counter = 0
                    st.session_state.widget_counter += 1
                    checkbox_key = f"select_{place_id}_{st.session_state.widget_counter}"
                    
                    is_selected = place_id in st.session_state.selected_dealers
                    new_selected = st.checkbox(
                        "Select",
                        value=is_selected,
                        key=checkbox_key,
                        label_visibility="collapsed"
                    )
                    
                    if new_selected != is_selected:
                        if new_selected:
                            if place_id not in st.session_state.selected_dealers:
                                st.session_state.selected_dealers.append(place_id)
                        else:
                            if place_id in st.session_state.selected_dealers:
                                st.session_state.selected_dealers.remove(place_id)
                        st.rerun()
            
            # Name and website column (adjusted for checkbox)
            with col2:
                name = _get_prospect_value(prospect, 'name', 'Unknown Dealership')
                st.markdown(f"### {name}")
                
                # Website link if available
                website = _get_prospect_value(prospect, 'website')
                if website:
                    if not website.startswith('http'):
                        website = f"https://{website}"
                    st.markdown(f"🌐 [Visit Website]({website}) ↗️")
            
            # Status column
            with col3:
                # Status badge
                st.markdown(f"""
                <div style="
                    background: {card_color};
                    color: white;
                    padding: 0.5rem;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                ">
                    {status.upper()}
                </div>
                """, unsafe_allow_html=True)
            
            # Visited column
            with col4:
                # Visited toggle
                if db_prospect:
                    # Create more robust unique key using a counter to avoid duplicates
                    if 'widget_counter' not in st.session_state:
                        st.session_state.widget_counter = 0
                    st.session_state.widget_counter += 1
                    unique_key = f"visited_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
                    new_visited = st.checkbox(
                        "Visited", 
                        value=visited,
                        key=unique_key
                    )
                    if new_visited != visited:
                        if crm_service:
                            crm_service.mark_prospect_visited(db_prospect.id, new_visited)
                        st.rerun()
        else:
            # Original layout without checkbox
            with col1:
                name = _get_prospect_value(prospect, 'name', 'Unknown Dealership')
                st.markdown(f"### {name}")
                
                # Website link if available
                website = _get_prospect_value(prospect, 'website')
                if website:
                    if not website.startswith('http'):
                        website = f"https://{website}"
                    st.markdown(f"🌐 [Visit Website]({website}) ↗️")
            
            with col2:
                # Status badge
                st.markdown(f"""
                <div style="
                    background: {card_color};
                    color: white;
                    padding: 0.5rem;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                ">
                    {status.upper()}
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Visited toggle
                if db_prospect:
                    # Create more robust unique key using a counter to avoid duplicates
                    if 'widget_counter' not in st.session_state:
                        st.session_state.widget_counter = 0
                    st.session_state.widget_counter += 1
                    unique_key = f"visited_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
                    new_visited = st.checkbox(
                        "Visited", 
                        value=visited,
                        key=unique_key
                    )
                    if new_visited != visited:
                        if crm_service:
                            crm_service.mark_prospect_visited(db_prospect.id, new_visited)
                        st.rerun()
        
        # Prospect details
        col1, col2 = st.columns(2)
        
        with col1:
            address = _get_prospect_value(prospect, 'address', 'N/A')
            phone = _get_prospect_value(prospect, 'phone', 'N/A')
            rating = _get_prospect_value(prospect, 'rating', 0)
            
            st.write(f"📍 **Address:** {address}")
            st.write(f"📞 **Phone:** {phone}")
            st.write(f"⭐ **Rating:** {rating:.1f}/5.0")
        
        with col2:
            distance = _get_prospect_value(prospect, 'distance_miles', 0)
            ai_score = _get_prospect_value(prospect, 'ai_score', 0)
            priority = _get_prospect_value(prospect, 'priority', 'standard')
            
            st.write(f"📏 **Distance:** {distance:.1f} miles")
            st.write(f"🤖 **AI Score:** {ai_score}/100")
            st.write(f"🎯 **Priority:** {priority.upper()}")
        
        # Notes section
        if db_prospect:
            st.markdown("#### 📝 Sales Notes")
            st.session_state.widget_counter += 1
            notes_key = f"notes_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            st.session_state.widget_counter += 1  
            save_notes_key = f"save_notes_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            notes = st.text_area(
                "Notes",
                value=db_prospect.sales_notes or "",
                height=100,
                key=f"notes_{notes_key}",
                label_visibility="collapsed"
            )
            
            if st.button("💾 Save Notes", key=f"save_notes_{save_notes_key}"):
                if crm_service:
                    crm_service.update_prospect_notes(db_prospect.id, notes)
                st.success("Notes saved!")
        
        # Communications panel
        if show_communications and db_prospect:
            with st.expander("📞 Communications", expanded=False):
                render_communication_panel(db_prospect.id, prospect, crm_service, communication_service)
        
        # Status update buttons
        if db_prospect:
            st.markdown("#### Status Actions")
            status_col1, status_col2, status_col3, status_col4, status_col5, status_col6 = st.columns(6)
            
            st.session_state.widget_counter += 1
            contacted_key = f"contacted_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            st.session_state.widget_counter += 1
            qualified_key = f"qualified_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            st.session_state.widget_counter += 1
            dnc_key = f"dnc_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            st.session_state.widget_counter += 1
            reset_key = f"reset_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            st.session_state.widget_counter += 1
            edit_contact_key = f"edit_contact_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            st.session_state.widget_counter += 1
            delete_key = f"delete_{db_prospect.id}_{db_prospect.place_id or 'no_place_id'}_{st.session_state.widget_counter}"
            
            with status_col1:
                if st.button("✅ Mark Contacted", key=f"contacted_{contacted_key}"):
                    if crm_service:
                        crm_service.update_prospect_status(db_prospect.id, 'contacted')
                    st.rerun()
            
            with status_col2:
                if st.button("🎯 Mark Qualified", key=f"qualified_{qualified_key}"):
                    if crm_service:
                        crm_service.update_prospect_status(db_prospect.id, 'qualified')
                    st.rerun()
            
            with status_col3:
                if st.button("🚫 Do Not Call", key=f"dnc_{dnc_key}"):
                    if crm_service:
                        crm_service.update_prospect_status(db_prospect.id, 'dnc')
                    st.rerun()
            
            with status_col4:
                if st.button("🔄 Reset Status", key=f"reset_{reset_key}"):
                    if crm_service:
                        crm_service.update_prospect_status(db_prospect.id, 'prospect')
                    st.rerun()
            
            with status_col5:
                if st.button("✏️ Edit Contact", key=f"edit_contact_{edit_contact_key}"):
                    # Toggle contact editing mode
                    edit_key = f"edit_contact_mode_{db_prospect.id}"
                    st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                    st.rerun()
            
            with status_col6:
                if st.button("🗑️ Delete", key=f"delete_{delete_key}", help="Permanently delete this prospect"):
                    # Confirmation dialog using session state
                    if f"confirm_delete_{db_prospect.id}" not in st.session_state:
                        st.session_state[f"confirm_delete_{db_prospect.id}"] = True
                        st.warning("⚠️ Click delete again to confirm permanent removal.")
                    else:
                        if crm_service and crm_service.delete_prospect(db_prospect.id):
                            st.success("✅ Prospect deleted successfully!")
                            # Clear confirmation state
                            del st.session_state[f"confirm_delete_{db_prospect.id}"]
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete prospect.")
        
        # Contact editing panel
        if db_prospect and st.session_state.get(f"edit_contact_mode_{db_prospect.id}", False):
            st.markdown("---")
            render_contact_info_editor(db_prospect)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_prospects_table(prospects: List, show_actions=True):
    """Render prospects in an interactive table"""
    
    if not prospects:
        st.info("No prospects found")
        return
    
    # Convert to DataFrame
    df_data = []
    for prospect in prospects:
        db_prospect = None
        if hasattr(prospect, 'id'):
            db_prospect = prospect
        else:
            place_id = _get_prospect_value(prospect, 'place_id')
            if place_id:
                db_prospect = crm_service.get_prospect_by_place_id(place_id) if crm_service else None
        
        row = {
            'ID': db_prospect.id if db_prospect else 0,
            'Name': _get_prospect_value(prospect, 'name', 'Unknown'),
            'Phone': _get_prospect_value(prospect, 'phone', 'N/A'),
            'Rating': _get_prospect_value(prospect, 'rating', 0),
            'Distance': _get_prospect_value(prospect, 'distance_miles', 0),
            'AI Score': _get_prospect_value(prospect, 'ai_score', 0),
            'Status': db_prospect.status if db_prospect else 'prospect',
            'Priority': db_prospect.priority if db_prospect else 'standard',
            'Visited': db_prospect.is_visited if db_prospect else False,
            'Website': _get_prospect_value(prospect, 'website', ''),
            'Last Updated': db_prospect.last_updated.strftime('%m/%d/%Y') if db_prospect and db_prospect.last_updated else 'N/A'
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Configure grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('single', use_checkbox=True)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
    
    # Column configurations
    gb.configure_column("Name", pinned='left', width=200)
    gb.configure_column("Phone", width=120)
    gb.configure_column("Rating", width=80, type=['numericColumn'], valueFormatter="value.toFixed(1)")
    gb.configure_column("Distance", width=100, type=['numericColumn'], valueFormatter="value.toFixed(1)")
    gb.configure_column("AI Score", width=100, type=['numericColumn'])
    gb.configure_column("Status", width=100)
    gb.configure_column("Priority", width=100)
    gb.configure_column("Visited", width=80, cellRenderer='checkboxRenderer')
    gb.configure_column("Website", width=150)
    gb.configure_column("Last Updated", width=120)
    
    gridOptions = gb.build()
    
    # Display grid
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        theme='streamlit',
        height=400,
        width='100%',
        reload_data=False
    )
    
    # Bulk delete functionality
    if len(df) > 0:
        st.markdown("---")
        bulk_col1, bulk_col2, bulk_col3 = st.columns([1, 1, 2])
        
        with bulk_col1:
            # Multi-select for bulk operations
            selected_ids = st.multiselect(
                "Select prospects to delete:",
                options=df[df['ID'] > 0]['ID'].tolist(),
                format_func=lambda x: f"ID {x}: {df[df['ID'] == x]['Name'].iloc[0] if len(df[df['ID'] == x]) > 0 else 'Unknown'}"
            )
        
        with bulk_col2:
            if selected_ids and st.button("🗑️ Delete Selected", type="secondary"):
                if "confirm_bulk_delete" not in st.session_state:
                    st.session_state.confirm_bulk_delete = True
                    st.warning(f"⚠️ Click again to confirm deletion of {len(selected_ids)} prospects.")
                else:
                    deleted_count = crm_service.bulk_delete_prospects(selected_ids) if crm_service else 0
                    if deleted_count > 0:
                        st.success(f"✅ Successfully deleted {deleted_count} prospects!")
                        del st.session_state.confirm_bulk_delete
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete prospects.")
        
        with bulk_col3:
            if selected_ids:
                st.info(f"Selected {len(selected_ids)} prospects for deletion")
    
    # Handle selection
    if grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
        try:
            selected_row = grid_response['selected_rows'].iloc[0] if hasattr(grid_response['selected_rows'], 'iloc') else grid_response['selected_rows'][0]
            prospect_id = selected_row['ID'] if isinstance(selected_row, dict) else getattr(selected_row, 'ID', 0)
        except (KeyError, IndexError, AttributeError):
            prospect_id = 0
        
        if prospect_id > 0:
            st.markdown("---")
            st.markdown("### Selected Prospect Details")
            
            db_prospect = crm_service.get_prospect_by_id(prospect_id) if crm_service else None
            if db_prospect:
                render_enhanced_prospect_card(db_prospect, show_communications=True)

def render_search_history_tab(crm_service=None):
    """Render the search history tab"""
    st.markdown("## 📊 Search History")
    
    if not crm_service:
        st.error("CRM service not available")
        return
    
    # Get search history
    searches = crm_service.get_search_history(limit=50)
    
    if not searches:
        st.info("No search history found. Perform some searches to see them here!")
        return
    
    # Search history table
    search_data = []
    for search in searches:
        search_data.append({
            'ID': search.id,
            'Date': search.created_at.strftime('%m/%d/%Y %H:%M'),
            'ZIP Codes': ', '.join(search.zip_codes) if search.zip_codes else 'N/A',
            'Radius': f"{search.radius_miles} miles",
            'Total Found': search.total_found,
            'New Prospects': search.new_prospects,
            'Duration': f"{search.search_duration_seconds:.1f}s" if search.search_duration_seconds else 'N/A'
        })
    
    df = pd.DataFrame(search_data)
    
    # Display with selection
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single', use_checkbox=True)
    gb.configure_column("Date", pinned='left', width=150)
    gb.configure_column("ZIP Codes", width=120)
    gb.configure_column("Radius", width=100)
    gb.configure_column("Total Found", width=120)
    gb.configure_column("New Prospects", width=130)
    gb.configure_column("Duration", width=100)
    
    gridOptions = gb.build()
    
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme='streamlit',
        height=300
    )
    
    # Handle search replay
    if grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
        try:
            selected_search = grid_response['selected_rows'].iloc[0] if hasattr(grid_response['selected_rows'], 'iloc') else grid_response['selected_rows'][0]
            search_id = selected_search['ID'] if isinstance(selected_search, dict) else getattr(selected_search, 'ID', 0)
        except (KeyError, IndexError, AttributeError):
            search_id = 0
        
        st.markdown("---")
        st.markdown("### Search Details")
        
        search = crm_service.get_search_by_id(search_id) if crm_service else None
        if search:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Search Date:** {search.created_at.strftime('%m/%d/%Y %H:%M')}")
                st.write(f"**ZIP Codes:** {', '.join(search.zip_codes) if search.zip_codes else 'N/A'}")
                st.write(f"**Radius:** {search.radius_miles} miles")
                st.write(f"**Min Rating:** {search.min_rating}")
            
            with col2:
                st.write(f"**Total Found:** {search.total_found}")
                st.write(f"**New Prospects:** {search.new_prospects}")
                st.write(f"**Duplicates:** {search.duplicate_prospects}")
                st.write(f"**Duration:** {search.search_duration_seconds:.1f}s" if search.search_duration_seconds else 'N/A')
            
            # AI Insights
            if search.ai_insights:
                st.markdown("#### 🤖 AI Insights")
                st.write(search.ai_insights)
            
            if search.territory_analysis:
                st.markdown("#### 📊 Territory Analysis")
                st.write(search.territory_analysis)
            
            with col3:
                # Delete search button
                if st.button("🗑️ Delete Search", key=f"delete_search_{search_id}", help="Delete this search from history"):
                    if f"confirm_delete_search_{search_id}" not in st.session_state:
                        st.session_state[f"confirm_delete_search_{search_id}"] = True
                        st.warning("⚠️ Click again to confirm deletion.")
                    else:
                        if crm_service and crm_service.delete_search(search_id):
                            st.success("✅ Search deleted from history!")
                            del st.session_state[f"confirm_delete_search_{search_id}"]
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete search.")
            
            # Replay button
            if st.button("🔄 Replay This Search", use_container_width=True):
                # Set session state to replay the search
                st.session_state.replay_search = {
                    'zip_codes': search.zip_codes,
                    'radius_miles': search.radius_miles,
                    'min_rating': search.min_rating
                }
                st.success("Search parameters loaded! Go to the Search tab to execute.")

def render_analytics_dashboard(crm_service=None):
    """Render the analytics dashboard"""
    st.markdown("## 📈 CRM Analytics")
    
    if not crm_service:
        st.error("CRM service not available")
        return
    
    # Get statistics
    prospect_stats = crm_service.get_prospect_stats()
    comm_stats = crm_service.get_communication_stats()
    territory_stats = crm_service.get_territory_stats()
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prospects", prospect_stats['total_prospects'])
    
    with col2:
        st.metric("Contacted", prospect_stats['contacted'])
    
    with col3:
        st.metric("Visited", prospect_stats['visited'])
    
    with col4:
        st.metric("Avg AI Score", f"{prospect_stats['avg_ai_score']:.1f}")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Status breakdown
        if prospect_stats['status_breakdown']:
            fig = px.pie(
                values=list(prospect_stats['status_breakdown'].values()),
                names=list(prospect_stats['status_breakdown'].keys()),
                title="Prospects by Status"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Communication breakdown
        if comm_stats['channel_breakdown']:
            fig = px.bar(
                x=list(comm_stats['channel_breakdown'].keys()),
                y=list(comm_stats['channel_breakdown'].values()),
                title="Communications by Channel (Last 30 Days)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Territory analysis
    if territory_stats:
        st.markdown("### 🗺️ Territory Performance")
        
        territory_df = pd.DataFrame(territory_stats)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                territory_df,
                x='prospect_count',
                y='avg_ai_score',
                size='visited_count',
                hover_data=['zip_code'],
                title="Territory Performance: Prospects vs AI Score"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                territory_df,
                x='zip_code',
                y='prospect_count',
                title="Prospects by ZIP Code"
            )
            st.plotly_chart(fig, use_container_width=True)

def render_contact_info_editor(prospect):
    """Render contact information editor for a prospect"""
    
    # Get current prospect from database
    db_prospect = None
    if hasattr(prospect, 'id'):
        db_prospect = prospect
    else:
        place_id = _get_prospect_value(prospect, 'place_id')
        if place_id:
            db_prospect = crm_service.get_prospect_by_place_id(place_id) if crm_service else None
    
    if not db_prospect:
        st.error("Cannot edit contact info - prospect not found in database")
        return
    
    st.markdown("### ✏️ Edit Contact Information")
    
    with st.form(f"contact_form_{db_prospect.id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Primary Contact")
            contact_person = st.text_input(
                "Contact Person",
                value=db_prospect.contact_person or "",
                help="Name of primary contact at dealership"
            )
            
            contact_title = st.text_input(
                "Title/Position",
                value=db_prospect.contact_title or "",
                help="Job title or position"
            )
            
            contact_email = st.text_input(
                "Email Address",
                value=db_prospect.contact_email or "",
                help="Primary email contact"
            )
        
        with col2:
            st.markdown("#### Dealership Information")
            phone = st.text_input(
                "Phone Number",
                value=db_prospect.phone or "",
                help="Primary dealership phone number"
            )
            
            website = st.text_input(
                "Website",
                value=db_prospect.website or "",
                help="Dealership website URL"
            )
            
            # Priority and AI score
            priority_options = ['low', 'standard', 'high']
            current_priority = db_prospect.priority or 'standard'
            priority = st.selectbox(
                "Priority Level",
                priority_options,
                index=priority_options.index(current_priority)
            )
        
        # Business hours (optional)
        st.markdown("#### Business Hours (Optional)")
        hours_col1, hours_col2 = st.columns(2)
        
        current_hours = db_prospect.business_hours or {}
        
        with hours_col1:
            monday_hours = st.text_input(
                "Monday",
                value=current_hours.get('monday', ''),
                placeholder="e.g., 9:00 AM - 6:00 PM"
            )
            tuesday_hours = st.text_input(
                "Tuesday", 
                value=current_hours.get('tuesday', ''),
                placeholder="e.g., 9:00 AM - 6:00 PM"
            )
            wednesday_hours = st.text_input(
                "Wednesday",
                value=current_hours.get('wednesday', ''),
                placeholder="e.g., 9:00 AM - 6:00 PM"
            )
            thursday_hours = st.text_input(
                "Thursday",
                value=current_hours.get('thursday', ''),
                placeholder="e.g., 9:00 AM - 6:00 PM"
            )
        
        with hours_col2:
            friday_hours = st.text_input(
                "Friday",
                value=current_hours.get('friday', ''),
                placeholder="e.g., 9:00 AM - 6:00 PM"
            )
            saturday_hours = st.text_input(
                "Saturday",
                value=current_hours.get('saturday', ''),
                placeholder="e.g., 9:00 AM - 5:00 PM"
            )
            sunday_hours = st.text_input(
                "Sunday",
                value=current_hours.get('sunday', ''),
                placeholder="e.g., 12:00 PM - 5:00 PM"
            )
        
        # Notes
        sales_notes = st.text_area(
            "Sales Notes",
            value=db_prospect.sales_notes or "",
            height=100,
            help="Internal notes about this prospect"
        )
        
        # Form submission
        submit_col1, submit_col2 = st.columns([1, 4])
        
        with submit_col1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        with submit_col2:
            if st.form_submit_button("🔄 Reset to Original", use_container_width=True):
                st.rerun()
        
        if submitted:
            # Compile business hours
            business_hours = {
                'monday': monday_hours,
                'tuesday': tuesday_hours,
                'wednesday': wednesday_hours,
                'thursday': thursday_hours,
                'friday': friday_hours,
                'saturday': saturday_hours,
                'sunday': sunday_hours
            }
            
            # Remove empty entries
            business_hours = {k: v for k, v in business_hours.items() if v.strip()}
            
            # Update prospect
            update_data = {
                'contact_person': contact_person.strip() if contact_person else None,
                'contact_title': contact_title.strip() if contact_title else None,
                'contact_email': contact_email.strip() if contact_email else None,
                'phone': phone.strip() if phone else None,
                'website': website.strip() if website else None,
                'priority': priority,
                'business_hours': business_hours if business_hours else None,
                'sales_notes': sales_notes.strip() if sales_notes else None
            }
            
            success = crm_service.update_prospect_contact_info(db_prospect.id, update_data) if crm_service else False
            
            if success:
                st.success("✅ Contact information updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update contact information")

def render_batch_messaging(crm_service=None, communication_service=None):
    """Render batch messaging interface with templates"""
    
    st.markdown("## 📨 Batch Messaging")
    
    if not crm_service:
        st.error("CRM service not available")
        return
    
    # Get all prospects for selection
    all_prospects = crm_service.get_all_prospects()
    
    if not all_prospects:
        st.info("No prospects found. Add some prospects first.")
        return
    
    # Prospect selection
    st.markdown("### 👥 Select Recipients")
    
    # Filter options
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ['prospect', 'contacted', 'qualified', 'visited', 'dnc'],
            default=['prospect', 'contacted', 'qualified']
        )
    
    with filter_col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            ['low', 'standard', 'high'],
            default=['standard', 'high']
        )
    
    with filter_col3:
        min_ai_score = st.slider(
            "Minimum AI Score",
            0, 100, 50,
            help="Only include prospects with AI score above this threshold"
        )
    
    # Apply filters
    filtered_prospects = [
        p for p in all_prospects
        if (p.status in status_filter if status_filter else True) and
           (p.priority in priority_filter if priority_filter else True) and
           (p.ai_score >= min_ai_score if p.ai_score else False)
    ]
    
    st.write(f"**{len(filtered_prospects)} prospects match your criteria**")
    
    # Manual selection
    if filtered_prospects:
        with st.expander("🎯 Manual Selection (Override Filters)", expanded=False):
            prospect_options = [f"{p.name} ({p.status}, AI: {p.ai_score})" for p in filtered_prospects]
            selected_indices = st.multiselect(
                "Select specific prospects:",
                range(len(prospect_options)),
                format_func=lambda i: prospect_options[i]
            )
            
            if selected_indices:
                filtered_prospects = [filtered_prospects[i] for i in selected_indices]
                st.write(f"**{len(filtered_prospects)} prospects manually selected**")
    
    if not filtered_prospects:
        st.warning("No prospects selected for messaging.")
        return
    
    # Channel selection
    st.markdown("### 📱 Select Communication Channel")
    
    channel_tab1, channel_tab2, channel_tab3 = st.tabs(["📧 Email", "💬 SMS", "📞 Call"])
    
    with channel_tab1:
        render_batch_email_interface(filtered_prospects)
    
    with channel_tab2:
        render_batch_sms_interface(filtered_prospects)
    
    with channel_tab3:
        render_batch_call_interface(filtered_prospects)

def render_batch_email_interface(prospects):
    """Render batch email interface"""
    
    st.markdown("#### 📧 Batch Email Campaign")
    
    # Template selection
    templates = communication_service.get_email_templates() if communication_service else []
    template_names = [t['name'] for t in templates]
    
    template_col1, template_col2 = st.columns([2, 1])
    
    with template_col1:
        selected_template = st.selectbox(
            "Choose Email Template",
            ["Custom"] + template_names
        )
    
    with template_col2:
        if st.button("📝 Manage Templates"):
            st.session_state.show_template_manager = True
    
    # Show template manager if requested
    if st.session_state.get('show_template_manager', False):
        render_template_manager('email')
        if st.button("✅ Done Managing Templates"):
            st.session_state.show_template_manager = False
            st.rerun()
        return
    
    # Template content
    if selected_template != "Custom":
        template = next(t for t in templates if t['name'] == selected_template)
        default_subject = template['subject']
        default_content = template['content']
    else:
        default_subject = "Partnership Opportunity with {{dealership_name}}"
        default_content = """Dear {{contact_name}},

I hope this message finds you well. My name is {{sender_name}} and I'm reaching out regarding a potential partnership opportunity for {{dealership_name}}.

{{custom_message}}

I'd love to schedule a brief conversation to discuss how we can help grow your business.

Best regards,
{{sender_name}}
{{sender_title}}
{{company_name}}
{{phone_number}}"""
    
    # Customization
    st.markdown("#### ✏️ Customize Message")
    
    subject = st.text_input("Subject Line", value=default_subject, key="email_subject")
    content = st.text_area("Email Content", value=default_content, height=200, key="email_content")
    
    # Personalization variables
    st.markdown("#### 🎨 Personalization")
    st.info("""
    **Available variables:**
    - `{{dealership_name}}` - Prospect's business name
    - `{{contact_name}}` - Contact person name (or 'Team' if not available)
    - `{{sender_name}}` - Your name
    - `{{sender_title}}` - Your job title
    - `{{company_name}}` - Your company name
    - `{{phone_number}}` - Your phone number
    - `{{custom_message}}` - Custom message per recipient
    """)
    
    # Sender information
    sender_col1, sender_col2 = st.columns(2)
    
    with sender_col1:
        sender_name = st.text_input("Your Name", value="Sales Representative", key="email_sender_name")
        sender_title = st.text_input("Your Title", value="Business Development", key="email_sender_title")
    
    with sender_col2:
        company_name = st.text_input("Company Name", value="Your Company", key="email_company_name")
        phone_number = st.text_input("Your Phone", value="(555) 123-4567", key="email_phone_number")
    
    # Custom message per type of dealership
    custom_message = st.text_area(
        "Custom Message (appears in {{custom_message}})",
        value="We specialize in helping independent dealerships like yours increase sales and improve customer experience through our proven automotive solutions.",
        height=100,
        key="email_custom_message"
    )
    
    # Preview
    st.markdown("#### 👀 Preview")
    
    if prospects:
        preview_prospect = prospects[0]
        preview_variables = {
            'dealership_name': preview_prospect.name,
            'contact_name': preview_prospect.contact_person or 'Team',
            'sender_name': sender_name,
            'sender_title': sender_title,
            'company_name': company_name,
            'phone_number': phone_number,
            'custom_message': custom_message
        }
        
        preview_subject = render_template_content(subject, preview_variables)
        preview_content = render_template_content(content, preview_variables)
        
        with st.expander("📧 Email Preview", expanded=True):
            st.write(f"**To:** {preview_prospect.contact_email or 'contact@dealership.com'}")
            st.write(f"**Subject:** {preview_subject}")
            st.markdown("**Content:**")
            st.markdown(preview_content.replace('\n', '<br>'), unsafe_allow_html=True)
    
    # Send options
    st.markdown("#### 🚀 Send Campaign")
    
    send_col1, send_col2 = st.columns([2, 1])
    
    with send_col1:
        send_immediately = st.checkbox("Send immediately", value=False)
        if not send_immediately:
            st.date_input("Schedule send date", value=datetime.now().date())
            st.time_input("Schedule send time", value=datetime.now().time())
            st.info("📅 Scheduled sending functionality coming soon - emails will be sent immediately for now.")
    
    with send_col2:
        test_email = st.text_input("Test email (optional)", key="email_test_email")
        if test_email and st.button("📧 Send Test"):
            # Send test email
            test_variables = {
                'dealership_name': 'Test Dealership',
                'contact_name': 'Test Contact',
                'sender_name': sender_name,
                'sender_title': sender_title,
                'company_name': company_name,
                'phone_number': phone_number,
                'custom_message': custom_message
            }
            
            test_subject = render_template_content(subject, test_variables)
            test_content = render_template_content(content, test_variables)
            
            if communication_service:
                result = communication_service.send_email(
                0,  # Test prospect ID
                test_email,
                f"[TEST] {test_subject}",
                test_content
            )
            
            if result['success']:
                st.success("Test email sent!")
            else:
                st.error(f"Test email failed: {result['error']}")
    
    # Launch campaign
    if st.button("🚀 Launch Email Campaign", type="primary", use_container_width=True):
        if not subject or not content:
            st.error("Please enter subject and content")
            return
        
        # Count prospects with valid emails
        valid_prospects = [p for p in prospects if p.contact_email]
        
        if not valid_prospects:
            st.error("No prospects have email addresses!")
            return
        
        st.info(f"Sending to {len(valid_prospects)} prospects with email addresses...")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        failure_count = 0
        
        # Send emails
        for i, prospect in enumerate(valid_prospects):
            variables = {
                'dealership_name': prospect.name,
                'contact_name': prospect.contact_person or 'Team',
                'sender_name': sender_name,
                'sender_title': sender_title,
                'company_name': company_name,
                'phone_number': phone_number,
                'custom_message': custom_message
            }
            
            final_subject = render_template_content(subject, variables)
            final_content = render_template_content(content, variables)
            
            if communication_service:
                result = communication_service.send_email(
                prospect.id,
                prospect.contact_email,
                final_subject,
                final_content
            )
            
            if result['success']:
                success_count += 1
            else:
                failure_count += 1
            
            # Update progress
            progress = (i + 1) / len(valid_prospects)
            progress_bar.progress(progress)
            status_text.text(f"Sent {i + 1}/{len(valid_prospects)} emails...")
        
        # Final results
        st.success(f"Campaign completed! ✅ {success_count} sent, ❌ {failure_count} failed")

def render_batch_sms_interface(prospects):
    """Render batch SMS interface"""
    
    st.markdown("#### 💬 Batch SMS Campaign")
    
    # Template selection
    templates = communication_service.get_sms_templates() if communication_service else []
    template_names = [t['name'] for t in templates]
    
    selected_template = st.selectbox(
        "Choose SMS Template",
        ["Custom"] + template_names
    )
    
    # Template content
    if selected_template != "Custom":
        template = next(t for t in templates if t['name'] == selected_template)
        default_message = template['message']
    else:
        default_message = "Hi {{contact_name}}! This is {{sender_name}} from {{company_name}}. I'd love to discuss how we can help {{dealership_name}} grow. Can we chat? {{phone_number}}"
    
    # Message customization
    message = st.text_area(
        "SMS Message (160 chars recommended)",
        value=default_message,
        max_chars=320,
        height=100,
        key="sms_message"
    )
    
    char_count = len(message)
    if char_count > 160:
        st.warning(f"Message is {char_count} characters. Will be sent as {(char_count // 160) + 1} parts.")
    else:
        st.info(f"Message length: {char_count}/160 characters")
    
    # Sender info
    sender_name = st.text_input("Your Name", value="Sales Rep", key="sms_sender_name")
    company_name = st.text_input("Company Name", value="Your Company", key="sms_company_name")
    phone_number = st.text_input("Your Phone", value="(555) 123-4567", key="sms_phone_number")
    
    # Preview
    if prospects:
        preview_prospect = prospects[0]
        preview_variables = {
            'dealership_name': preview_prospect.name,
            'contact_name': preview_prospect.contact_person or 'there',
            'sender_name': sender_name,
            'company_name': company_name,
            'phone_number': phone_number
        }
        
        preview_message = render_template_content(message, preview_variables)
        
        with st.expander("💬 SMS Preview", expanded=True):
            st.write(f"**To:** {preview_prospect.phone or '(555) 123-4567'}")
            st.markdown(f"**Message:** {preview_message}")
    
    # Send campaign
    if st.button("🚀 Launch SMS Campaign", type="primary", use_container_width=True):
        valid_prospects = [p for p in prospects if p.phone]
        
        if not valid_prospects:
            st.error("No prospects have phone numbers!")
            return
        
        st.info(f"Sending to {len(valid_prospects)} prospects with phone numbers...")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        failure_count = 0
        
        for i, prospect in enumerate(valid_prospects):
            variables = {
                'dealership_name': prospect.name,
                'contact_name': prospect.contact_person or 'there',
                'sender_name': sender_name,
                'company_name': company_name,
                'phone_number': phone_number
            }
            
            final_message = render_template_content(message, variables)
            
            result = communication_service.send_sms(
                prospect.id,
                prospect.phone,
                final_message
            )
            
            if result['success']:
                success_count += 1
            else:
                failure_count += 1
            
            progress = (i + 1) / len(valid_prospects)
            progress_bar.progress(progress)
            status_text.text(f"Sent {i + 1}/{len(valid_prospects)} SMS messages...")
        
        st.success(f"Campaign completed! ✅ {success_count} sent, ❌ {failure_count} failed")

def render_batch_call_interface(prospects):
    """Render batch call interface"""
    
    st.markdown("#### 📞 Batch Call Campaign")
    
    # Call script
    call_script = st.text_area(
        "Call Script / Notes",
        value="""Hi, this is {{sender_name}} from {{company_name}}. 

I'm calling because I specialize in helping independent dealerships like {{dealership_name}} increase their sales and improve their customer experience.

I'd love to schedule a brief 15-minute conversation to discuss some strategies that have worked well for similar dealerships in your area.

Would you be available for a quick call this week?""",
        height=150,
        key="call_script"
    )
    
    # Sender info
    sender_name = st.text_input("Your Name", value="Sales Representative", key="call_sender_name")
    company_name = st.text_input("Company Name", value="Your Company", key="call_company_name")
    
    # Call scheduling
    st.markdown("#### ⏰ Call Scheduling")
    
    immediate_calls = st.checkbox("Make calls immediately (requires Twilio configuration)")
    
    if not immediate_calls:
        st.info("📝 Calls will be logged as 'scheduled' and you can make them manually using the call script.")
    
    # Preview
    if prospects:
        preview_prospect = prospects[0]
        preview_variables = {
            'dealership_name': preview_prospect.name,
            'sender_name': sender_name,
            'company_name': company_name
        }
        
        preview_script = render_template_content(call_script, preview_variables)
        
        with st.expander("📞 Call Script Preview", expanded=True):
            st.write(f"**Calling:** {preview_prospect.name}")
            st.write(f"**Phone:** {preview_prospect.phone or '(555) 123-4567'}")
            st.markdown("**Script:**")
            st.markdown(preview_script.replace('\n', '<br>'), unsafe_allow_html=True)
    
    # Launch campaign
    if st.button("🚀 Launch Call Campaign", type="primary", use_container_width=True):
        valid_prospects = [p for p in prospects if p.phone]
        
        if not valid_prospects:
            st.error("No prospects have phone numbers!")
            return
        
        st.info(f"Processing {len(valid_prospects)} prospects with phone numbers...")
        
        success_count = 0
        failure_count = 0
        
        for prospect in valid_prospects:
            variables = {
                'dealership_name': prospect.name,
                'sender_name': sender_name,
                'company_name': company_name
            }
            
            final_script = render_template_content(call_script, variables)
            
            if immediate_calls:
                # Attempt to make actual call
                result = communication_service.make_call(
                    prospect.id,
                    prospect.phone,
                    final_script
                )
                
                if result['success']:
                    success_count += 1
                else:
                    failure_count += 1
            else:
                # Log as scheduled call
                comm_data = {
                    'channel': 'call',
                    'direction': 'outbound',
                    'status': 'scheduled',
                    'message': final_script
                }
                crm_service.log_communication(prospect.id, comm_data)
                success_count += 1
        
        if immediate_calls:
            st.success(f"Campaign completed! ✅ {success_count} calls initiated, ❌ {failure_count} failed")
        else:
            st.success(f"Campaign scheduled! ✅ {success_count} calls logged for manual follow-up")

def render_template_manager(channel_type):
    """Render template management interface"""
    
    st.markdown(f"### 📝 Manage {channel_type.title()} Templates")
    
    # Get existing templates
    if channel_type == 'email':
        templates = communication_service.get_email_templates() if communication_service else []
    else:
        templates = communication_service.get_sms_templates() if communication_service else []
    
    # Create new template
    with st.expander("➕ Create New Template", expanded=False):
        with st.form("new_template"):
            template_name = st.text_input("Template Name")
            
            if channel_type == 'email':
                template_subject = st.text_input("Subject")
                template_content = st.text_area("Content", height=150)
            else:
                template_content = st.text_area("Message", height=100, max_chars=320)
                template_subject = None
            
            if st.form_submit_button("💾 Save Template"):
                if template_name and template_content:
                    template_data = {
                        'name': template_name,
                        'content': template_content
                    }
                    if template_subject:
                        template_data['subject'] = template_subject
                    
                    # Save template (implement in communication service)
                    st.success(f"Template '{template_name}' created!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields")
    
    # Edit existing templates
    if templates:
        st.markdown("#### Existing Templates")
        
        for template in templates:
            with st.expander(f"📄 {template['name']}", expanded=False):
                st.write(f"**Content:** {template.get('content', template.get('message', ''))[:100]}...")
                
                if st.button("🗑️ Delete", key=f"del_{template['name']}"):
                    st.warning("Template deletion would be implemented here")
    else:
        st.info("No templates found. Create your first template above!")

def render_template_content(template: str, variables: dict) -> str:
    """Render template with variable substitution"""
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result 