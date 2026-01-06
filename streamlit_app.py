import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import json
import base64

# Page configuration
st.set_page_config(
    page_title="Sofia Vet Platform",
    page_icon="🐱",
    layout="wide"
)

# Translation dictionary (keeping your existing translations)
TRANSLATIONS = {
    'en': {
        # Page titles
        'app_title': 'Sofia Vet Platform',
        'app_subtitle': 'Find the best veterinary clinic for your pet',
        'navigation': 'Navigation',
        'search_clinics': 'Search Clinics',
        'add_clinic': 'Add Clinic',
        'add_review': 'Add Review',
        'view_all_clinics': 'View All Clinics',
        
        # Search page
        'search_header': 'Search for Veterinary Clinics',
        'your_location': 'Your Location (Optional)',
        'location_help': 'Enter your location to find the nearest clinics and see distances',
        'your_latitude': 'Your Latitude',
        'your_longitude': 'Your Longitude',
        'max_distance': 'Max Distance (km)',
        'search_by_location': 'Search by location (find nearest clinics)',
        'search_filters': 'Search Filters',
        'quick_searches': 'Quick Searches (Click to auto-fill)',
        'common_searches': 'Common Searches:',
        'hotels_btn': 'Hotels',
        'vaccination_btn': 'Vaccination',
        'diagnostics_btn': 'Diagnostics',
        'emergency_btn': 'Emergency',
        'services': 'Services',
        'equipment': 'Equipment',
        'available': 'available',
        'select_services': 'Select services (leave empty for all)',
        'select_equipment': 'Select equipment (leave empty for all)',
        'service_help': 'Select one or more services you\'re looking for',
        'equipment_help': 'Select equipment the clinic should have',
        'emergency_care': 'Emergency Care',
        'inpatient_care': 'Inpatient Care',
        'wild_animal_care': 'Wild Animal Care',
        'minimum_rating': 'Minimum rating',
        'search_btn': 'Search',
        'clear_btn': 'Clear',
        'found_clinics': 'Found {count} clinic(s)',
        'active_filters': 'Active Filters:',
        'rating_filter': 'Rating',
        'clinic_locations': 'Clinic Locations',
        'clinic_details': 'Clinic Details',
        'no_clinics_found': 'No clinics found matching your criteria',
        'adjust_filters': 'Try adjusting your search filters or expanding the search radius.',
        'use_search_filters': 'Use the search filters above and click \'Search\' to find veterinary clinics',
        'km_away': '{distance:.2f} km away',
        
        # Clinic details
        'contact_info': 'Contact Information',
        'address': 'Address',
        'phone': 'Phone',
        'email': 'Email',
        'location': 'Location',
        'coordinates': 'Coordinates',
        'distance_from_you': 'Distance from you',
        'services_offered': 'Services Offered',
        'equipment_available': 'Equipment Available',
        'lab_tests': 'Laboratory Tests',
        'not_specified': 'Not specified',
        'and_more': '...and {count} more',
        'standard_care': 'Standard Care',
        
        # Add clinic page
        'register_clinic': 'Register New Clinic',
        'basic_info': 'Basic Information',
        'clinic_name': 'Clinic Name*',
        'clinic_name_placeholder': 'e.g., Sofia Pet Care',
        'address_placeholder': 'e.g., 123 Main St, Sofia',
        'phone_placeholder': 'e.g., +359 2 123 4567',
        'email_placeholder': 'e.g., info@sofiavetcare.com',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'care_types': 'Care Types Available',
        'services_offered_label': 'Services Offered',
        'other_services': 'Other Services (comma-separated)',
        'other_services_placeholder': 'e.g., behavioral training, nutritional counseling',
        'equipment_available_label': 'Equipment Available',
        'other_equipment': 'Other Equipment (comma-separated)',
        'other_equipment_placeholder': 'e.g., ECG machine, anesthesia machine',
        'lab_tests_label': 'Laboratory Tests Available',
        'lab_tests_placeholder': 'Blood tests\nUrine analysis\nFecal examination\nBiochemistry panel\nX-ray imaging\nUltrasound diagnostics',
        
        # Service name translations
        'service_cat_hotel': 'Cat Hotel',
        'service_dog_hotel': 'Dog Hotel',
        'service_grooming': 'Grooming',
        'service_deworming': 'Deworming',
        'service_prophylaxis': 'Prophylaxis',
        'service_dental_care': 'Dental Care',
        'service_surgery': 'Surgery',
        'service_vaccination': 'Vaccination',
        'service_ophthalmology': 'Ophthalmology',
        'service_microchipping': 'Microchipping',
        'service_travel_documents': 'Travel Documents',
        
        # Equipment name translations
        'equipment_xray': 'X-Ray',
        'equipment_ultrasound': 'Ultrasound',
        'equipment_incubator': 'Incubator',
        'equipment_oxygen': 'Oxygen Machine',
        'register_btn': 'Register Clinic',
        'clinic_registered': 'Clinic \'{name}\' registered successfully!',
        'added_items': 'Added {services} services, {equipment} equipment items, and {tests} lab tests.',
        'fill_required': 'Please fill in all required fields (marked with *)',
        'registration_error': 'Error registering clinic: {error}',
        'check_db': 'Please check if the database has the correct structure. Try deleting vet_platform.db and restart the app.',
        
        # Review page
        'add_review_header': 'Add a Review',
        'select_clinic': 'Select Clinic',
        'rating': 'Rating',
        'your_review': 'Your review',
        'review_placeholder': 'Share your experience...',
        'submit_review': 'Submit Review',
        'review_submitted': 'Review submitted successfully!',
        'no_clinics_yet': 'No clinics available yet. Please add a clinic first.',
        
        # View all page
        'all_clinics_header': 'All Registered Clinics',
        'clinics_list': 'Clinics List',
        'clinic_name_col': 'Clinic Name',
        'address_col': 'Address',
        'phone_col': 'Phone',
        'rating_col': 'Rating',
        'care_types_col': 'Care Types Available',
        'detailed_info': 'Detailed Clinic Information',
        'select_clinic_details': 'Select a clinic to view details:',
        'clinic_location': 'Clinic Location',
        'platform_stats': 'Platform Statistics',
        'total_clinics': 'Total Clinics',
        'average_rating': 'Average Rating',
        'emergency_clinics': 'Emergency Clinics',
        'inpatient_clinics': 'Inpatient Care',
        'no_clinics_registered': 'No clinics registered yet. Add your first clinic!',
        
        # Backup features
        'backup_restore': 'Backup & Restore',
        'download_backup': 'Download Database Backup',
        'upload_backup': 'Upload Database Backup',
        'backup_success': 'Database backed up successfully!',
        'restore_success': 'Database restored successfully!',
        'restore_error': 'Error restoring database',
        
        # About
        'about': 'About',
        'about_text': 'Sofia Vet Platform - Find the best veterinary care for your pet. Search clinics by services, location, and ratings.',
    },
    'bg': {
        # (keeping existing Bulgarian translations for brevity)
        'app_title': 'София Вет Платформа',
        # ... add all other Bulgarian translations from your original file
    }
}

def t(key, lang=None, **kwargs):
    """Translation helper function"""
    if lang is None:
        lang = st.session_state.get('language', 'en')
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def translate_service_name(english_name, lang):
    """Translate service name from English to selected language"""
    service_map = {
        'Cat Hotel': 'service_cat_hotel',
        'Dog Hotel': 'service_dog_hotel',
        'Grooming': 'service_grooming',
        'Deworming': 'service_deworming',
        'Prophylaxis': 'service_prophylaxis',
        'Dental Care': 'service_dental_care',
        'Surgery': 'service_surgery',
        'Vaccination': 'service_vaccination',
        'Ophthalmology': 'service_ophthalmology',
        'Microchipping': 'service_microchipping',
        'Travel Documents': 'service_travel_documents',
    }
    
    key = service_map.get(english_name)
    if key:
        return t(key, lang)
    else:
        return english_name

def translate_equipment_name(english_name, lang):
    """Translate equipment name from English to selected language"""
    equipment_map = {
        'X-Ray': 'equipment_xray',
        'Ultrasound': 'equipment_ultrasound',
        'Incubator': 'equipment_incubator',
        'Oxygen Machine': 'equipment_oxygen',
    }
    
    key = equipment_map.get(english_name)
    if key:
        return t(key, lang)
    else:
        return english_name

# Database connection with persistent path
DB_PATH = os.path.join(os.path.dirname(__file__), "vet_platform.db")

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    try:
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    except:
        return None

def create_clinic_map(clinics_df, user_location=None, zoom_start=12):
    """Create a folium map with clinic markers"""
    # Default center (Sofia, Bulgaria)
    center_lat = 42.6977
    center_lon = 23.3219
    
    if user_location:
        center_lat, center_lon = user_location
    elif len(clinics_df) > 0:
        center_lat = clinics_df['latitude'].mean()
        center_lon = clinics_df['longitude'].mean()
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    # Add user location marker if provided
    if user_location:
        folium.Marker(
            location=user_location,
            popup="Your Location",
            tooltip="You are here",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)
    
    # Add clinic markers
    for _, clinic in clinics_df.iterrows():
        if pd.notna(clinic['latitude']) and pd.notna(clinic['longitude']):
            # Create popup content
            popup_html = f"""
            <div style='font-family: Arial; width: 200px;'>
                <h4>{clinic['name']}</h4>
                <p><b>Rating:</b> ⭐ {clinic['rating']:.1f}</p>
                <p><b>Address:</b> {clinic['address']}</p>
                <p><b>Phone:</b> {clinic['phone']}</p>
            """
            
            badges = []
            if clinic.get('emergency_available', 0):
                badges.append('🚨 Emergency')
            if clinic.get('inpatient_care', 0):
                badges.append('🏨 Inpatient')
            if clinic.get('wild_animal_care', 0):
                badges.append('🦊 Wild Animal')
            
            if badges:
                popup_html += f"<p><b>Care Types:</b><br>{'<br>'.join(badges)}</p>"
            
            popup_html += "</div>"
            
            # Choose marker color based on rating
            if clinic['rating'] >= 4.5:
                color = 'green'
            elif clinic['rating'] >= 3.5:
                color = 'blue'
            else:
                color = 'gray'
            
            # Add marker
            folium.Marker(
                location=[clinic['latitude'], clinic['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=clinic['name'],
                icon=folium.Icon(color=color, icon='plus', prefix='fa')
            ).add_to(m)
    
    return m

def get_table_columns(table_name):
    """Get column names for a table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns
    except:
        return []

def init_db():
    """Initialize database - create tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables (basic structure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            email TEXT,
            latitude REAL,
            longitude REAL,
            rating REAL DEFAULT 0,
            emergency_available INTEGER DEFAULT 0,
            inpatient_care INTEGER DEFAULT 0,
            wild_animal_care INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinic_id INTEGER,
            service_name TEXT NOT NULL,
            price REAL,
            FOREIGN KEY (clinic_id) REFERENCES clinics (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinic_id INTEGER,
            equipment_name TEXT NOT NULL,
            FOREIGN KEY (clinic_id) REFERENCES clinics (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinic_id INTEGER,
            test_name TEXT NOT NULL,
            FOREIGN KEY (clinic_id) REFERENCES clinics (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinic_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (clinic_id) REFERENCES clinics (id)
        )
    """)
    
    # Add new columns to existing clinics table if they don't exist
    try:
        cursor.execute("ALTER TABLE clinics ADD COLUMN inpatient_care INTEGER DEFAULT 0")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE clinics ADD COLUMN wild_animal_care INTEGER DEFAULT 0")
    except:
        pass
    
    conn.commit()
    conn.close()

def backup_database():
    """Create a backup of the database as JSON"""
    conn = get_db_connection()
    
    # Export all tables
    backup_data = {
        'clinics': pd.read_sql_query("SELECT * FROM clinics", conn).to_dict('records'),
        'services': pd.read_sql_query("SELECT * FROM services", conn).to_dict('records'),
        'equipment': pd.read_sql_query("SELECT * FROM equipment", conn).to_dict('records'),
        'lab_tests': pd.read_sql_query("SELECT * FROM lab_tests", conn).to_dict('records'),
        'reviews': pd.read_sql_query("SELECT * FROM reviews", conn).to_dict('records'),
        'backup_date': datetime.now().isoformat()
    }
    
    conn.close()
    return json.dumps(backup_data, indent=2)

def restore_database(backup_json):
    """Restore database from JSON backup"""
    try:
        backup_data = json.loads(backup_json)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM reviews")
        cursor.execute("DELETE FROM lab_tests")
        cursor.execute("DELETE FROM equipment")
        cursor.execute("DELETE FROM services")
        cursor.execute("DELETE FROM clinics")
        
        # Restore clinics
        for clinic in backup_data.get('clinics', []):
            columns = ', '.join(clinic.keys())
            placeholders = ', '.join(['?' for _ in clinic])
            cursor.execute(f"INSERT INTO clinics ({columns}) VALUES ({placeholders})", list(clinic.values()))
        
        # Restore services
        for service in backup_data.get('services', []):
            columns = ', '.join(service.keys())
            placeholders = ', '.join(['?' for _ in service])
            cursor.execute(f"INSERT INTO services ({columns}) VALUES ({placeholders})", list(service.values()))
        
        # Restore equipment
        for equip in backup_data.get('equipment', []):
            columns = ', '.join(equip.keys())
            placeholders = ', '.join(['?' for _ in equip])
            cursor.execute(f"INSERT INTO equipment ({columns}) VALUES ({placeholders})", list(equip.values()))
        
        # Restore lab_tests
        for test in backup_data.get('lab_tests', []):
            columns = ', '.join(test.keys())
            placeholders = ', '.join(['?' for _ in test])
            cursor.execute(f"INSERT INTO lab_tests ({columns}) VALUES ({placeholders})", list(test.values()))
        
        # Restore reviews
        for review in backup_data.get('reviews', []):
            columns = ', '.join(review.keys())
            placeholders = ', '.join(['?' for _ in review])
            cursor.execute(f"INSERT INTO reviews ({columns}) VALUES ({placeholders})", list(review.values()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error restoring database: {e}")
        return False

# Initialize database
init_db()

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Language selector in sidebar
st.sidebar.markdown("---")
col_lang1, col_lang2 = st.sidebar.columns(2)
with col_lang1:
    if st.button("🇬🇧 English", use_container_width=True, type="primary" if st.session_state.language == 'en' else "secondary"):
        st.session_state.language = 'en'
        st.rerun()
with col_lang2:
    if st.button("🇧🇬 Български", use_container_width=True, type="primary" if st.session_state.language == 'bg' else "secondary"):
        st.session_state.language = 'bg'
        st.rerun()

lang = st.session_state.language

# Main app
st.title(t('app_title', lang))
st.markdown(f"### {t('app_subtitle', lang)}")

# Sidebar navigation
st.sidebar.title(t('navigation', lang))
page = st.sidebar.radio(
    "",
    [
        t('search_clinics', lang),
        t('add_clinic', lang),
        t('add_review', lang),
        t('view_all_clinics', lang),
        t('backup_restore', lang)
    ]
)

# Backup & Restore Page (NEW!)
if page == t('backup_restore', lang):
    st.header("💾 " + t('backup_restore', lang))
    
    st.markdown("""
    ### Why do I need this?
    If you're running this app on Streamlit Cloud or another hosting service, the database file 
    gets deleted when the app restarts or sleeps. Use these features to save and restore your data:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 " + t('download_backup', lang))
        st.markdown("Download a backup of your entire database (all clinics, reviews, etc.)")
        
        if st.button("Create Backup", type="primary"):
            backup_json = backup_database()
            b64 = base64.b64encode(backup_json.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="vet_platform_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json">Click here to download backup</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success(t('backup_success', lang))
    
    with col2:
        st.subheader("📤 " + t('upload_backup', lang))
        st.markdown("Restore your database from a previously downloaded backup file")
        
        uploaded_file = st.file_uploader("Choose a backup file", type=['json'])
        if uploaded_file is not None:
            if st.button("Restore from Backup", type="secondary"):
                backup_content = uploaded_file.read().decode('utf-8')
                if restore_database(backup_content):
                    st.success(t('restore_success', lang))
                    st.rerun()
                else:
                    st.error(t('restore_error', lang))
    
    st.markdown("---")
    st.info("💡 **Tip:** Download backups regularly to keep your data safe!")

# Search Clinics Page
elif page == t('search_clinics', lang):
    st.header(f"🔍 {t('search_header', lang)}")
    
    # Location input
    with st.expander(t('your_location', lang), expanded=False):
        st.markdown(t('location_help', lang))
        col1, col2, col3 = st.columns(3)
        with col1:
            user_lat = st.number_input(t('your_latitude', lang), value=42.6977, format="%.6f")
        with col2:
            user_lon = st.number_input(t('your_longitude', lang), value=23.3219, format="%.6f")
        with col3:
            max_distance = st.number_input(t('max_distance', lang), value=50.0, min_value=1.0, max_value=500.0)
        
        use_location = st.checkbox(t('search_by_location', lang), value=False)
    
    st.markdown(f"### {t('search_filters', lang)}")
    
    # Quick search buttons
    st.markdown(f"#### {t('quick_searches', lang)}")
    st.caption(t('common_searches', lang))
    col1, col2, col3, col4 = st.columns(4)
    
    # Initialize session state for quick searches
    if 'quick_search_services' not in st.session_state:
        st.session_state.quick_search_services = []
    if 'quick_search_equipment' not in st.session_state:
        st.session_state.quick_search_equipment = []
    if 'quick_search_emergency' not in st.session_state:
        st.session_state.quick_search_emergency = False
    
    with col1:
        if st.button("🏨 " + t('hotels_btn', lang), use_container_width=True):
            st.session_state.quick_search_services = ['Cat Hotel', 'Dog Hotel']
            st.rerun()
    with col2:
        if st.button("💉 " + t('vaccination_btn', lang), use_container_width=True):
            st.session_state.quick_search_services = ['Vaccination']
            st.rerun()
    with col3:
        if st.button("🔬 " + t('diagnostics_btn', lang), use_container_width=True):
            st.session_state.quick_search_equipment = ['X-Ray', 'Ultrasound']
            st.rerun()
    with col4:
        if st.button("🚨 " + t('emergency_btn', lang), use_container_width=True):
            st.session_state.quick_search_emergency = True
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{t('services', lang)}** {t('available', lang)}")
        
        # Get available services
        conn = get_db_connection()
        services_df = pd.read_sql_query("SELECT DISTINCT service_name FROM services ORDER BY service_name", conn)
        conn.close()
        
        if len(services_df) > 0:
            service_list = services_df['service_name'].tolist()
            
            # Create translated options for display
            service_options_translated = [translate_service_name(s, lang) for s in service_list]
            
            # Create mapping for reverse lookup
            service_display_to_english = {
                translate_service_name(s, lang): s 
                for s in service_list
            }
            
            # Use quick search if available
            default_services_english = [s for s in st.session_state.quick_search_services if s in service_list]
            default_services_translated = [translate_service_name(s, lang) for s in default_services_english]
            
            selected_services_display = st.multiselect(
                t('select_services', lang),
                options=service_options_translated,
                default=default_services_translated,
                help=t('service_help', lang),
                key='services_multi'
            )
            
            # Convert displayed names back to English
            selected_services = [
                service_display_to_english[s] 
                for s in selected_services_display
            ]
            
            # Clear quick search after use
            if default_services_english:
                st.session_state.quick_search_services = []
        else:
            selected_services = []
            st.info(t('no_clinics_yet', lang))
    
    with col2:
        st.markdown(f"**{t('equipment', lang)}** {t('available', lang)}")
        
        # Get available equipment
        conn = get_db_connection()
        equipment_df = pd.read_sql_query("SELECT DISTINCT equipment_name FROM equipment ORDER BY equipment_name", conn)
        conn.close()
        
        if len(equipment_df) > 0:
            equipment_list = equipment_df['equipment_name'].tolist()
            
            # Create translated options for display
            equipment_options_translated = [translate_equipment_name(e, lang) for e in equipment_list]
            
            # Create mapping for reverse lookup
            equipment_display_to_english = {
                translate_equipment_name(e, lang): e 
                for e in equipment_list
            }
            
            # Use quick search if available
            default_equipment_english = [e for e in st.session_state.quick_search_equipment if e in equipment_list]
            default_equipment_translated = [translate_equipment_name(e, lang) for e in default_equipment_english]
            
            selected_equipment_display = st.multiselect(
                t('select_equipment', lang),
                options=equipment_options_translated,
                default=default_equipment_translated,
                help=t('equipment_help', lang),
                key='equipment_multi'
            )
            
            # Convert displayed names back to English
            selected_equipment = [
                equipment_display_to_english[e] 
                for e in selected_equipment_display
            ]
            
            # Clear quick search after use
            if default_equipment_english:
                st.session_state.quick_search_equipment = []
        else:
            selected_equipment = []
    
    # Additional filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        emergency_default = st.session_state.quick_search_emergency
        emergency_only = st.checkbox(t('emergency_care', lang), value=emergency_default)
        if emergency_default:
            st.session_state.quick_search_emergency = False
    with col2:
        inpatient_only = st.checkbox(t('inpatient_care', lang))
    with col3:
        wild_animal_only = st.checkbox(t('wild_animal_care', lang))
    
    min_rating = st.slider(t('minimum_rating', lang), 0.0, 5.0, 0.0, 0.5)
    
    col1, col2 = st.columns(2)
    with col1:
        search_clicked = st.button(t('search_btn', lang), type="primary", use_container_width=True)
    with col2:
        if st.button(t('clear_btn', lang), use_container_width=True):
            st.session_state.quick_search_services = []
            st.session_state.quick_search_equipment = []
            st.session_state.quick_search_emergency = False
            st.rerun()
    
    if search_clicked:
        # Build query
        query = """
            SELECT DISTINCT c.*, 
                   GROUP_CONCAT(DISTINCT s.service_name) as services,
                   GROUP_CONCAT(DISTINCT e.equipment_name) as equipment,
                   GROUP_CONCAT(DISTINCT l.test_name) as lab_tests
            FROM clinics c
            LEFT JOIN services s ON c.id = s.clinic_id
            LEFT JOIN equipment e ON c.id = e.clinic_id
            LEFT JOIN lab_tests l ON c.id = l.clinic_id
            WHERE 1=1
        """
        
        params = []
        
        if selected_services:
            service_conditions = " OR ".join(["s.service_name = ?" for _ in selected_services])
            query += f" AND c.id IN (SELECT clinic_id FROM services WHERE {service_conditions})"
            params.extend(selected_services)
        
        if selected_equipment:
            equipment_conditions = " OR ".join(["e.equipment_name = ?" for _ in selected_equipment])
            query += f" AND c.id IN (SELECT clinic_id FROM equipment WHERE {equipment_conditions})"
            params.extend(selected_equipment)
        
        if emergency_only:
            query += " AND c.emergency_available = 1"
        
        if inpatient_only:
            query += " AND c.inpatient_care = 1"
        
        if wild_animal_only:
            query += " AND c.wild_animal_care = 1"
        
        if min_rating > 0:
            query += " AND c.rating >= ?"
            params.append(min_rating)
        
        query += " GROUP BY c.id ORDER BY c.rating DESC"
        
        conn = get_db_connection()
        results = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Filter by distance if location is enabled
        if use_location and len(results) > 0:
            results['distance'] = results.apply(
                lambda row: calculate_distance(user_lat, user_lon, row['latitude'], row['longitude'])
                if pd.notna(row['latitude']) and pd.notna(row['longitude']) else None,
                axis=1
            )
            results = results[results['distance'] <= max_distance]
            results = results.sort_values('distance')
        
        # Display results
        st.markdown("---")
        st.subheader(t('found_clinics', lang, count=len(results)))
        
        if len(results) > 0:
            # Show active filters
            active_filters = []
            if selected_services:
                active_filters.append(f"{t('services', lang)}: {', '.join(selected_services)}")
            if selected_equipment:
                active_filters.append(f"{t('equipment', lang)}: {', '.join(selected_equipment)}")
            if emergency_only:
                active_filters.append(t('emergency_care', lang))
            if inpatient_only:
                active_filters.append(t('inpatient_care', lang))
            if wild_animal_only:
                active_filters.append(t('wild_animal_care', lang))
            if min_rating > 0:
                active_filters.append(f"{t('rating_filter', lang)} ≥ {min_rating}")
            
            if active_filters:
                st.info(f"**{t('active_filters', lang)}** {', '.join(active_filters)}")
            
            # Show map
            st.markdown(f"### 🗺️ {t('clinic_locations', lang)}")
            user_location = (user_lat, user_lon) if use_location else None
            search_map = create_clinic_map(results, user_location=user_location, zoom_start=12)
            st_folium(search_map, width=None, height=500)
            
            # Show clinic details
            st.markdown(f"### 📋 {t('clinic_details', lang)}")
            
            for idx, clinic in results.iterrows():
                with st.expander(f"**{clinic['name']}** - ⭐ {clinic['rating']:.1f}" + 
                               (f" - 📍 {t('km_away', lang, distance=clinic['distance'])}" if use_location and pd.notna(clinic.get('distance')) else "")):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**{t('contact_info', lang)}**")
                        st.write(f"**{t('address', lang)}:** {clinic['address']}")
                        st.write(f"**{t('phone', lang)}:** {clinic['phone']}")
                        st.write(f"**{t('email', lang)}:** {clinic['email']}")
                        
                        if pd.notna(clinic['latitude']) and pd.notna(clinic['longitude']):
                            st.write(f"**{t('coordinates', lang)}:** {clinic['latitude']:.6f}, {clinic['longitude']:.6f}")
                        
                        if use_location and pd.notna(clinic.get('distance')):
                            st.write(f"**{t('distance_from_you', lang)}:** {clinic['distance']:.2f} km")
                        
                        # Care types
                        care_types = []
                        if clinic.get('emergency_available', 0):
                            care_types.append('🚨 Emergency')
                        if clinic.get('inpatient_care', 0):
                            care_types.append('🏨 Inpatient')
                        if clinic.get('wild_animal_care', 0):
                            care_types.append('🦊 Wild Animal')
                        
                        if care_types:
                            st.markdown("**Care Types:**")
                            for ct in care_types:
                                st.write(f"• {ct}")
                    
                    with col2:
                        st.markdown(f"**{t('services_offered', lang)}**")
                        if clinic['services']:
                            services = clinic['services'].split(',')
                            for svc in services[:5]:
                                translated_svc = translate_service_name(svc.strip(), lang)
                                st.write(f"• {translated_svc}")
                            if len(services) > 5:
                                st.write(t('and_more', lang, count=len(services)-5))
                        else:
                            st.write(f"*{t('not_specified', lang)}*")
                        
                        st.markdown(f"**{t('equipment_available', lang)}**")
                        if clinic['equipment']:
                            equipment_list = clinic['equipment'].split(',')
                            for eq in equipment_list[:5]:
                                translated_eq = translate_equipment_name(eq.strip(), lang)
                                st.write(f"• {translated_eq}")
                            if len(equipment_list) > 5:
                                st.write(t('and_more', lang, count=len(equipment_list)-5))
                        else:
                            st.write(f"*{t('not_specified', lang)}*")
        else:
            st.warning(t('no_clinics_found', lang))
            st.info(t('adjust_filters', lang))
    else:
        st.info(t('use_search_filters', lang))

# Add Clinic Page
elif page == t('add_clinic', lang):
    st.header(f"➕ {t('register_clinic', lang)}")
    
    with st.form("add_clinic_form"):
        st.subheader(t('basic_info', lang))
        
        name = st.text_input(t('clinic_name', lang), placeholder=t('clinic_name_placeholder', lang))
        address = st.text_input(t('address', lang), placeholder=t('address_placeholder', lang))
        
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input(t('phone', lang), placeholder=t('phone_placeholder', lang))
        with col2:
            email = st.text_input(t('email', lang), placeholder=t('email_placeholder', lang))
        
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input(t('latitude', lang), value=42.6977, format="%.6f")
        with col2:
            longitude = st.number_input(t('longitude', lang), value=23.3219, format="%.6f")
        
        st.markdown("---")
        
        st.markdown(f"### {t('care_types', lang)}")
        col1, col2, col3 = st.columns(3)
        with col1:
            emergency = st.checkbox(t('emergency_care', lang))
        with col2:
            inpatient = st.checkbox(t('inpatient_care', lang))
        with col3:
            wild_animal = st.checkbox(t('wild_animal_care', lang))
        
        st.markdown("---")
        
        st.markdown(f"### {t('services_offered_label', lang)}")
        
        service_options = [
            "Cat Hotel", "Dog Hotel", "Grooming", "Deworming", 
            "Prophylaxis", "Dental Care", "Surgery", "Vaccination",
            "Ophthalmology", "Microchipping", "Travel Documents"
        ]
        
        # Create a grid of checkboxes for services
        cols = st.columns(3)
        selected_services = []
        for idx, service in enumerate(service_options):
            with cols[idx % 3]:
                # Display translated name but store English name in database
                translated_name = translate_service_name(service, lang)
                if st.checkbox(translated_name, key=f"service_{service}"):
                    selected_services.append(service)  # Store English name
        
        other_services = st.text_input(
            f"➕ {t('other_services', lang)}", 
            placeholder=t('other_services_placeholder', lang)
        )
        
        st.markdown("---")
        
        st.markdown(f"### {t('equipment_available_label', lang)}")
        
        equipment_options = ["X-Ray", "Ultrasound", "Incubator", "Oxygen Machine"]
        
        cols = st.columns(4)
        selected_equipment = []
        for idx, equip in enumerate(equipment_options):
            with cols[idx]:
                # Display translated name but store English name in database
                translated_name = translate_equipment_name(equip, lang)
                if st.checkbox(translated_name, key=f"equip_{equip}"):
                    selected_equipment.append(equip)  # Store English name
        
        other_equipment = st.text_input(
            f"➕ {t('other_equipment', lang)}", 
            placeholder=t('other_equipment_placeholder', lang)
        )
        
        st.markdown("---")
        
        st.markdown(f"### {t('lab_tests_label', lang)}")
        lab_tests = st.text_area(
            t('lab_tests_label', lang),
            placeholder=t('lab_tests_placeholder', lang),
            height=150
        )
        
        submitted = st.form_submit_button(t('register_btn', lang), type="primary", use_container_width=True)
        
        if submitted:
            if not name or not address:
                st.error(t('fill_required', lang))
            else:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Insert clinic
                    cursor.execute("""
                        INSERT INTO clinics (name, address, phone, email, latitude, longitude, 
                                           emergency_available, inpatient_care, wild_animal_care)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, address, phone, email, latitude, longitude, 
                         1 if emergency else 0, 1 if inpatient else 0, 1 if wild_animal else 0))
                    
                    clinic_id = cursor.lastrowid
                    
                    # Add services
                    all_services = selected_services.copy()
                    if other_services:
                        all_services.extend([s.strip() for s in other_services.split(',')])
                    
                    for service in all_services:
                        if service:
                            cursor.execute("INSERT INTO services (clinic_id, service_name) VALUES (?, ?)", 
                                         (clinic_id, service))
                    
                    # Add equipment
                    all_equipment = selected_equipment.copy()
                    if other_equipment:
                        all_equipment.extend([e.strip() for e in other_equipment.split(',')])
                    
                    for equip in all_equipment:
                        if equip:
                            cursor.execute("INSERT INTO equipment (clinic_id, equipment_name) VALUES (?, ?)", 
                                         (clinic_id, equip))
                    
                    # Add lab tests
                    test_list = []
                    if lab_tests:
                        test_list = [t.strip() for t in lab_tests.split('\n') if t.strip()]
                        for test in test_list:
                            cursor.execute("INSERT INTO lab_tests (clinic_id, test_name) VALUES (?, ?)", 
                                         (clinic_id, test))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(t('clinic_registered', lang, name=name))
                    st.info(t('added_items', lang, services=len(all_services), 
                            equipment=len(all_equipment), tests=len(test_list)))
                    
                except Exception as e:
                    st.error(t('registration_error', lang, error=str(e)))
                    st.info(t('check_db', lang))

# Add Review Page
elif page == t('add_review', lang):
    st.header(f"⭐ {t('add_review_header', lang)}")
    
    conn = get_db_connection()
    clinics = pd.read_sql_query("SELECT id, name FROM clinics ORDER BY name", conn)
    conn.close()
    
    if len(clinics) > 0:
        with st.form("add_review_form"):
            clinic_options = {row['name']: row['id'] for _, row in clinics.iterrows()}
            selected_clinic = st.selectbox(t('select_clinic', lang), options=list(clinic_options.keys()))
            
            rating = st.slider(t('rating', lang), 1, 5, 5)
            comment = st.text_area(t('your_review', lang), placeholder=t('review_placeholder', lang))
            
            submitted = st.form_submit_button(t('submit_review', lang))
            
            if submitted:
                clinic_id = clinic_options[selected_clinic]
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Insert review
                cursor.execute("""
                    INSERT INTO reviews (clinic_id, rating, comment)
                    VALUES (?, ?, ?)
                """, (clinic_id, rating, comment))
                
                # Update clinic average rating
                cursor.execute("""
                    UPDATE clinics
                    SET rating = (
                        SELECT AVG(rating) FROM reviews WHERE clinic_id = ?
                    )
                    WHERE id = ?
                """, (clinic_id, clinic_id))
                
                conn.commit()
                conn.close()
                
                st.success(t('review_submitted', lang))
    else:
        st.info(t('no_clinics_yet', lang))

# View All Clinics Page
elif page == t('view_all_clinics', lang):
    st.header(f"📊 {t('all_clinics_header', lang)}")
    
    conn = get_db_connection()
    clinics = pd.read_sql_query("""
        SELECT c.*, 
               COUNT(DISTINCT r.id) as review_count,
               GROUP_CONCAT(DISTINCT s.service_name) as services,
               GROUP_CONCAT(DISTINCT e.equipment_name) as equipment,
               GROUP_CONCAT(DISTINCT l.test_name) as lab_tests
        FROM clinics c
        LEFT JOIN reviews r ON c.id = r.clinic_id
        LEFT JOIN services s ON c.id = s.clinic_id
        LEFT JOIN equipment e ON c.id = e.clinic_id
        LEFT JOIN lab_tests l ON c.id = l.clinic_id
        GROUP BY c.id
        ORDER BY c.rating DESC, c.name
    """, conn)
    conn.close()
    
    if len(clinics) > 0:
        # Display map first
        st.subheader(f"🗺️ {t('clinic_locations', lang)}")
        all_clinics_map = create_clinic_map(clinics, zoom_start=11)
        st_folium(all_clinics_map, width=None, height=500)
        
        st.markdown("---")
        
        # Add care type columns for display
        clinics['care_types'] = clinics.apply(
            lambda row: ', '.join([
                '🚨 Emergency' if row.get('emergency_available', 0) else '',
                '🏨 Inpatient' if row.get('inpatient_care', 0) else '',
                '🦊 Wild Animal' if row.get('wild_animal_care', 0) else ''
            ]).strip(', ') or t('standard_care', lang),
            axis=1
        )
        
        # Display main table
        st.subheader(f"📋 {t('clinics_list', lang)}")
        display_cols = ['name', 'address', 'phone', 'rating', 'care_types']
        st.dataframe(
            clinics[display_cols], 
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": t('clinic_name_col', lang),
                "address": t('address_col', lang),
                "phone": t('phone_col', lang),
                "rating": st.column_config.NumberColumn(t('rating_col', lang), format="⭐ %.1f"),
                "care_types": t('care_types_col', lang)
            }
        )
        
        # Detailed view option
        st.markdown("---")
        st.subheader(f"🔍 {t('detailed_info', lang)}")
        
        selected_clinic_name = st.selectbox(
            t('select_clinic_details', lang),
            options=clinics['name'].tolist()
        )
        
        if selected_clinic_name:
            clinic = clinics[clinics['name'] == selected_clinic_name].iloc[0]
            
            # Show map for individual clinic
            if pd.notna(clinic['latitude']) and pd.notna(clinic['longitude']):
                st.markdown(f"#### 📍 {t('clinic_location', lang)}")
                clinic_df = pd.DataFrame([clinic])
                single_clinic_map = create_clinic_map(clinic_df, zoom_start=15)
                st_folium(single_clinic_map, width=None, height=300)
                st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📍 {t('contact_info', lang)}**")
                st.write(f"{t('address', lang)}: {clinic['address']}")
                st.write(f"{t('phone', lang)}: {clinic['phone']}")
                st.write(f"{t('email', lang)}: {clinic['email']}")
                st.write(f"{t('rating', lang)}: ⭐ {clinic['rating']:.1f}")
                st.write(f"{t('coordinates', lang)}: {clinic['latitude']:.6f}, {clinic['longitude']:.6f}")
                
                st.markdown(f"**🏥 {t('care_types', lang)}**")
                st.write(clinic['care_types'])
            
            with col2:
                st.markdown(f"**💉 {t('services_offered', lang)}**")
                if clinic['services']:
                    for svc in clinic['services'].split(','):
                        translated_svc = translate_service_name(svc.strip(), lang)
                        st.write(f"• {translated_svc}")
                else:
                    st.write(f"*{t('not_specified', lang)}*")
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown(f"**🔬 {t('equipment_available', lang)}**")
                if clinic['equipment']:
                    for eq in clinic['equipment'].split(','):
                        translated_eq = translate_equipment_name(eq.strip(), lang)
                        st.write(f"• {translated_eq}")
                else:
                    st.write(f"*{t('not_specified', lang)}*")
            
            with col4:
                st.markdown(f"**🧪 {t('lab_tests', lang)}**")
                if clinic['lab_tests']:
                    for lab in clinic['lab_tests'].split(','):
                        st.write(f"• {lab}")
                else:
                    st.write(f"*{t('not_specified', lang)}*")
        
        # Statistics
        st.markdown("---")
        st.subheader(f"📈 {t('platform_stats', lang)}")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(t('total_clinics', lang), len(clinics))
        
        with col2:
            st.metric(t('average_rating', lang), f"{clinics['rating'].mean():.2f}")
        
        with col3:
            emergency_count = clinics['emergency_available'].sum()
            st.metric(f"🚨 {t('emergency_clinics', lang)}", int(emergency_count))
        
        with col4:
            inpatient_count = clinics.get('inpatient_care', pd.Series([0])).sum()
            st.metric(f"🏨 {t('inpatient_clinics', lang)}", int(inpatient_count))
    else:
        st.info(t('no_clinics_registered', lang))

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t('about', lang)}")
st.sidebar.info(t('about_text', lang))
