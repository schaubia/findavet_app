import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Page configuration
st.set_page_config(
    page_title="Sofia Vet Platform",
    page_icon="🐱",
    layout="wide"
)

# Database connection
DB_PATH = "vet_platform.db"

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
            <div style="width: 250px;">
                <h4>{clinic['name']}</h4>
                <p><b>Rating:</b> ⭐ {clinic['rating']:.1f}</p>
                <p><b>Address:</b> {clinic['address']}</p>
                <p><b>Phone:</b> {clinic['phone']}</p>
            """
            
            if 'distance' in clinic and pd.notna(clinic['distance']):
                popup_html += f"<p><b>Distance:</b> {clinic['distance']:.2f} km</p>"
            
            # Add care type badges
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

# Initialize database
init_db()

# Title
st.title("🐱 Sofia Vet Platform")
st.markdown("### Find the best veterinary clinic for your pet")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Search Clinics", "Add Clinic", "Add Review", "View All Clinics"])

# Search Clinics Page
if page == "Search Clinics":
    st.header("🔍 Search for Veterinary Clinics")
    
    # Initialize session state for search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_user_location' not in st.session_state:
        st.session_state.search_user_location = None
    
    # Location input section
    st.subheader("📍 Your Location (Optional)")
    st.markdown("*Enter your location to find the nearest clinics and see distances*")
    
    col_loc1, col_loc2, col_loc3 = st.columns([2, 2, 1])
    
    with col_loc1:
        user_lat = st.number_input("Your Latitude", value=42.6977, format="%.6f", help="Sofia center: 42.6977")
    
    with col_loc2:
        user_lon = st.number_input("Your Longitude", value=23.3219, format="%.6f", help="Sofia center: 23.3219")
    
    with col_loc3:
        max_distance = st.number_input("Max Distance (km)", value=50.0, min_value=1.0, max_value=200.0, step=5.0)
    
    use_location = st.checkbox("🎯 Search by location (find nearest clinics)", value=False)
    
    st.markdown("---")
    
    # Get available services and equipment from database for autocomplete
    conn = get_db_connection()
    all_services = pd.read_sql_query("""
        SELECT DISTINCT service_name 
        FROM services 
        WHERE service_name IS NOT NULL 
        ORDER BY service_name
    """, conn)
    all_equipment = pd.read_sql_query("""
        SELECT DISTINCT equipment_name 
        FROM equipment 
        WHERE equipment_name IS NOT NULL 
        ORDER BY equipment_name
    """, conn)
    conn.close()
    
    service_options = all_services['service_name'].tolist()
    equipment_options = all_equipment['equipment_name'].tolist()
    
    # Search filters
    st.subheader("🔍 Search Filters")
    
    # Quick search shortcuts
    with st.expander("⚡ Quick Searches (Click to auto-fill)", expanded=False):
        st.markdown("**Common Searches:**")
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        
        with col_q1:
            if st.button("🏨 Hotels", use_container_width=True):
                st.session_state.quick_search_services = ["Cat Hotel", "Dog Hotel"]
        with col_q2:
            if st.button("💉 Vaccination", use_container_width=True):
                st.session_state.quick_search_services = ["Vaccination"]
        with col_q3:
            if st.button("🔬 Diagnostics", use_container_width=True):
                st.session_state.quick_search_equipment = ["X-Ray", "Ultrasound"]
        with col_q4:
            if st.button("🚨 Emergency", use_container_width=True):
                st.session_state.quick_search_emergency = True
    
    # Initialize quick search session state
    if 'quick_search_services' not in st.session_state:
        st.session_state.quick_search_services = []
    if 'quick_search_equipment' not in st.session_state:
        st.session_state.quick_search_equipment = []
    if 'quick_search_emergency' not in st.session_state:
        st.session_state.quick_search_emergency = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**💉 Services** ({len(service_options)} available)")
        if len(service_options) > 0:
            # Use quick search if available
            default_services = [s for s in st.session_state.quick_search_services if s in service_options]
            selected_services = st.multiselect(
                "Select services (leave empty for all)",
                options=service_options,
                default=default_services,
                help="Select one or more services you're looking for"
            )
            # Clear quick search after use
            if default_services:
                st.session_state.quick_search_services = []
        else:
            st.warning("No services registered yet. Add clinics with services first.")
            selected_services = []
    
    with col2:
        st.markdown(f"**🔬 Equipment** ({len(equipment_options)} available)")
        if len(equipment_options) > 0:
            # Use quick search if available
            default_equipment = [e for e in st.session_state.quick_search_equipment if e in equipment_options]
            selected_equipment = st.multiselect(
                "Select equipment (leave empty for all)",
                options=equipment_options,
                default=default_equipment,
                help="Select equipment the clinic should have"
            )
            # Clear quick search after use
            if default_equipment:
                st.session_state.quick_search_equipment = []
        else:
            st.warning("No equipment registered yet. Add clinics with equipment first.")
            selected_equipment = []
    
    col3, col4 = st.columns(2)
    
    with col3:
        emergency_default = st.session_state.quick_search_emergency
        emergency_only = st.checkbox("🚨 Emergency Care", value=emergency_default)
        if emergency_default:
            st.session_state.quick_search_emergency = False  # Reset after use
        inpatient_only = st.checkbox("🏨 Inpatient Care")
    
    with col4:
        wild_animal_only = st.checkbox("🦊 Wild Animal Care")
        min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, 0.5)
    
    # Search and Clear buttons
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")
    with col_btn2:
        clear_clicked = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_clicked:
        st.session_state.search_results = None
        st.session_state.search_user_location = None
        st.rerun()
    
    if search_clicked:
        conn = get_db_connection()
        
        # Build query with subqueries for service and equipment filtering
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
        
        # Filter by selected services (clinic must have ALL selected services)
        if selected_services:
            service_conditions = []
            for service in selected_services:
                service_conditions.append("""
                    c.id IN (
                        SELECT clinic_id FROM services WHERE service_name = ?
                    )
                """)
                params.append(service)
            query += " AND " + " AND ".join(service_conditions)
        
        # Filter by selected equipment (clinic must have ALL selected equipment)
        if selected_equipment:
            equipment_conditions = []
            for equip in selected_equipment:
                equipment_conditions.append("""
                    c.id IN (
                        SELECT clinic_id FROM equipment WHERE equipment_name = ?
                    )
                """)
                params.append(equip)
            query += " AND " + " AND ".join(equipment_conditions)
        
        if emergency_only:
            query += " AND c.emergency_available = 1"
        
        if inpatient_only:
            query += " AND c.inpatient_care = 1"
        
        if wild_animal_only:
            query += " AND c.wild_animal_care = 1"
        
        query += " AND c.rating >= ?"
        params.append(min_rating)
        
        query += " GROUP BY c.id"
        
        results = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Calculate distances if location search is enabled
        if use_location and len(results) > 0:
            results['distance'] = results.apply(
                lambda row: calculate_distance(user_lat, user_lon, row['latitude'], row['longitude']),
                axis=1
            )
            # Filter by max distance
            results = results[results['distance'] <= max_distance]
            # Sort by distance
            results = results.sort_values('distance')
        else:
            # Sort by rating if not using location
            results = results.sort_values('rating', ascending=False)
        
        # Store results in session state
        st.session_state.search_results = results
        st.session_state.search_user_location = (user_lat, user_lon) if use_location else None
    
    # Display results from session state
    if st.session_state.search_results is not None:
        results = st.session_state.search_results
        user_location = st.session_state.search_user_location
        
        if len(results) > 0:
            st.success(f"Found {len(results)} clinic(s)")
            
            # Show active filters
            active_filters = []
            if selected_services:
                active_filters.append(f"**Services:** {', '.join(selected_services)}")
            if selected_equipment:
                active_filters.append(f"**Equipment:** {', '.join(selected_equipment)}")
            if emergency_only:
                active_filters.append("**🚨 Emergency Care**")
            if inpatient_only:
                active_filters.append("**🏨 Inpatient Care**")
            if wild_animal_only:
                active_filters.append("**🦊 Wild Animal Care**")
            if min_rating > 0:
                active_filters.append(f"**Rating:** ≥ {min_rating:.1f}")
            if user_location:
                active_filters.append(f"**Max Distance:** {max_distance} km")
            
            if active_filters:
                st.info("**Active Filters:** " + " | ".join(active_filters))
            
            # Display map
            st.subheader("🗺️ Clinic Locations")
            clinic_map = create_clinic_map(results, user_location=user_location)
            st_folium(clinic_map, width=None, height=500)
            
            st.markdown("---")
            st.subheader("📋 Clinic Details")
            
            for idx, (_, clinic) in enumerate(results.iterrows(), 1):
                # Create care type badges
                care_badges = []
                if clinic.get('emergency_available', 0):
                    care_badges.append("🚨 Emergency")
                if clinic.get('inpatient_care', 0):
                    care_badges.append("🏨 Inpatient")
                if clinic.get('wild_animal_care', 0):
                    care_badges.append("🦊 Wild Animal")
                
                badge_str = " | ".join(care_badges) if care_badges else "Standard Care"
                
                # Add distance to title if available
                title = f"#{idx} ⭐ {clinic['name']} - Rating: {clinic['rating']:.1f}"
                if 'distance' in clinic and pd.notna(clinic['distance']):
                    title += f" | 📍 {clinic['distance']:.2f} km away"
                title += f" | {badge_str}"
                
                with st.expander(title):
                    # Contact Info
                    st.markdown("#### 📍 Contact Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Address:** {clinic['address']}")
                        st.write(f"**Phone:** {clinic['phone']}")
                    
                    with col2:
                        st.write(f"**Email:** {clinic['email']}")
                        st.write(f"**Location:** {clinic['latitude']:.4f}, {clinic['longitude']:.4f}")
                        if 'distance' in clinic and pd.notna(clinic['distance']):
                            st.write(f"**Distance from you:** {clinic['distance']:.2f} km")
                    
                    st.markdown("---")
                    
                    # Services, Equipment, Lab Tests
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("#### 💉 Services")
                        if clinic['services']:
                            services_list = clinic['services'].split(',')
                            for svc in services_list[:5]:  # Show first 5
                                st.write(f"• {svc}")
                            if len(services_list) > 5:
                                st.write(f"*...and {len(services_list) - 5} more*")
                        else:
                            st.write("*Not specified*")
                    
                    with col2:
                        st.markdown("#### 🔬 Equipment")
                        if clinic['equipment']:
                            equip_list = clinic['equipment'].split(',')
                            for eq in equip_list:
                                st.write(f"• {eq}")
                        else:
                            st.write("*Not specified*")
                    
                    with col3:
                        st.markdown("#### 🧪 Lab Tests")
                        if clinic['lab_tests']:
                            lab_list = clinic['lab_tests'].split(',')
                            for lab in lab_list[:5]:  # Show first 5
                                st.write(f"• {lab}")
                            if len(lab_list) > 5:
                                st.write(f"*...and {len(lab_list) - 5} more*")
                        else:
                            st.write("*Not specified*")
        else:
            st.warning("No clinics found matching your criteria")
            st.info("Try adjusting your search filters or expanding the search radius.")
    else:
        st.info("👆 Use the search filters above and click 'Search' to find veterinary clinics")


# Add Clinic Page
elif page == "Add Clinic":
    st.header("🏥 Register New Clinic")
    
    with st.form("add_clinic_form"):
        # Basic Information
        st.subheader("Basic Information")
        name = st.text_input("Clinic Name*", placeholder="e.g., Sofia Pet Care")
        address = st.text_input("Address*", placeholder="e.g., 123 Main St, Sofia")
        phone = st.text_input("Phone", placeholder="e.g., +359 2 123 4567")
        email = st.text_input("Email", placeholder="e.g., info@sofiavetcare.com")
        
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=42.6977, format="%.6f")
        with col2:
            longitude = st.number_input("Longitude", value=23.3219, format="%.6f")
        
        st.markdown("---")
        
        # Care Types
        st.subheader("🏥 Care Types Available")
        col1, col2, col3 = st.columns(3)
        with col1:
            emergency = st.checkbox("🚨 Emergency Care")
        with col2:
            inpatient = st.checkbox("🏨 Inpatient Care")
        with col3:
            wild_animal = st.checkbox("🦊 Wild Animal Care")
        
        st.markdown("---")
        
        # Services
        st.subheader("💉 Services Offered")
        
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
                if st.checkbox(service, key=f"service_{service}"):
                    selected_services.append(service)
        
        # Other services input
        other_services = st.text_input("➕ Other Services (comma-separated)", 
                                      placeholder="e.g., behavioral training, nutritional counseling")
        
        st.markdown("---")
        
        # Equipment
        st.subheader("🔬 Equipment Available")
        
        equipment_options = ["X-Ray", "Ultrasound", "Incubator", "Oxygen Machine"]
        
        cols = st.columns(4)
        selected_equipment = []
        for idx, equip in enumerate(equipment_options):
            with cols[idx]:
                if st.checkbox(equip, key=f"equip_{equip}"):
                    selected_equipment.append(equip)
        
        other_equipment = st.text_input("➕ Other Equipment (comma-separated)", 
                                       placeholder="e.g., ECG machine, anesthesia machine")
        
        st.markdown("---")
        
        # Laboratory Tests
        st.subheader("🧪 Laboratory Tests Available")
        lab_tests = st.text_area("Laboratory Tests (one per line)", 
                                 placeholder="Blood tests\nUrine analysis\nFecal examination\nBiochemistry panel\nX-ray imaging\nUltrasound diagnostics",
                                 height=150)
        
        submitted = st.form_submit_button("✅ Register Clinic", use_container_width=True)
        
        if submitted:
            if name and address:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Convert booleans to integers for SQLite
                    emergency_int = 1 if emergency else 0
                    inpatient_int = 1 if inpatient else 0
                    wild_animal_int = 1 if wild_animal else 0
                    
                    # Get available columns
                    columns = get_table_columns('clinics')
                    
                    # Build insert query based on available columns
                    insert_cols = ['name', 'address']
                    insert_vals = [name, address]
                    
                    if phone and 'phone' in columns:
                        insert_cols.append('phone')
                        insert_vals.append(phone)
                    
                    if email and 'email' in columns:
                        insert_cols.append('email')
                        insert_vals.append(email)
                    
                    if 'latitude' in columns:
                        insert_cols.append('latitude')
                        insert_vals.append(latitude)
                    
                    if 'longitude' in columns:
                        insert_cols.append('longitude')
                        insert_vals.append(longitude)
                    
                    if 'emergency_available' in columns:
                        insert_cols.append('emergency_available')
                        insert_vals.append(emergency_int)
                    
                    if 'inpatient_care' in columns:
                        insert_cols.append('inpatient_care')
                        insert_vals.append(inpatient_int)
                    
                    if 'wild_animal_care' in columns:
                        insert_cols.append('wild_animal_care')
                        insert_vals.append(wild_animal_int)
                    
                    # Insert clinic
                    placeholders = ', '.join(['?'] * len(insert_vals))
                    cols_str = ', '.join(insert_cols)
                    
                    cursor.execute(f"""
                        INSERT INTO clinics ({cols_str})
                        VALUES ({placeholders})
                    """, tuple(insert_vals))
                    
                    clinic_id = cursor.lastrowid
                
                    # Insert services
                    all_services = selected_services.copy()
                    if other_services:
                        all_services.extend([s.strip() for s in other_services.split(',') if s.strip()])
                    
                    for service in all_services:
                        cursor.execute("""
                            INSERT INTO services (clinic_id, service_name)
                            VALUES (?, ?)
                        """, (clinic_id, service))
                    
                    # Insert equipment
                    all_equipment = selected_equipment.copy()
                    if other_equipment:
                        all_equipment.extend([e.strip() for e in other_equipment.split(',') if e.strip()])
                    
                    for equip in all_equipment:
                        cursor.execute("""
                            INSERT INTO equipment (clinic_id, equipment_name)
                            VALUES (?, ?)
                        """, (clinic_id, equip))
                    
                    # Insert lab tests
                    if lab_tests:
                        test_list = [t.strip() for t in lab_tests.split('\n') if t.strip()]
                        for test in test_list:
                            cursor.execute("""
                                INSERT INTO lab_tests (clinic_id, test_name)
                                VALUES (?, ?)
                            """, (clinic_id, test))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Clinic '{name}' registered successfully!")
                    st.info(f"Added {len(all_services)} services, {len(all_equipment)} equipment items, and {len(test_list) if lab_tests else 0} lab tests.")
                    
                except Exception as e:
                    st.error(f"Error registering clinic: {str(e)}")
                    st.info("Please check if the database has the correct structure. Try deleting vet_platform.db and restart the app.")
            else:
                st.error("Please fill in all required fields (marked with *)")

# Add Review Page
elif page == "Add Review":
    st.header("⭐ Add a Review")
    
    conn = get_db_connection()
    clinics = pd.read_sql_query("SELECT id, name FROM clinics ORDER BY name", conn)
    conn.close()
    
    if len(clinics) > 0:
        with st.form("add_review_form"):
            clinic_options = {row['name']: row['id'] for _, row in clinics.iterrows()}
            selected_clinic = st.selectbox("Select Clinic", options=list(clinic_options.keys()))
            
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Your review", placeholder="Share your experience...")
            
            submitted = st.form_submit_button("Submit Review")
            
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
                
                st.success("✅ Review submitted successfully!")
    else:
        st.info("No clinics available yet. Please add a clinic first.")

# View All Clinics Page
elif page == "View All Clinics":
    st.header("📊 All Registered Clinics")
    
    conn = get_db_connection()
    clinics = pd.read_sql_query("""
        SELECT c.*, 
               COUNT(DISTINCT r.id) as review_count,
               GROUP_CONCAT(DISTINCT s.service_name) as services,
               GROUP_CONCAT(DISTINCT e.equipment_name) as equipment,
               GROUP_CONCAT(DISTINCT l.test_name) as lab_tests
        FROM clinics c
        LEFT JOIN reviews r ON c.id = r.id
        LEFT JOIN services s ON c.id = s.clinic_id
        LEFT JOIN equipment e ON c.id = e.clinic_id
        LEFT JOIN lab_tests l ON c.id = l.clinic_id
        GROUP BY c.id
        ORDER BY c.rating DESC, c.name
    """, conn)
    conn.close()
    
    if len(clinics) > 0:
        # Display map first
        st.subheader("🗺️ All Clinic Locations")
        all_clinics_map = create_clinic_map(clinics, zoom_start=11)
        st_folium(all_clinics_map, width=None, height=500)
        
        st.markdown("---")
        
        # Add care type columns for display
        clinics['care_types'] = clinics.apply(
            lambda row: ', '.join([
                '🚨 Emergency' if row.get('emergency_available', 0) else '',
                '🏨 Inpatient' if row.get('inpatient_care', 0) else '',
                '🦊 Wild Animal' if row.get('wild_animal_care', 0) else ''
            ]).strip(', ') or 'Standard',
            axis=1
        )
        
        # Display main table
        st.subheader("📋 Clinics List")
        display_cols = ['name', 'address', 'phone', 'rating', 'care_types']
        st.dataframe(
            clinics[display_cols], 
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": "Clinic Name",
                "address": "Address",
                "phone": "Phone",
                "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
                "care_types": "Care Types Available"
            }
        )
        
        # Detailed view option
        st.markdown("---")
        st.subheader("🔍 Detailed Clinic Information")
        
        selected_clinic_name = st.selectbox(
            "Select a clinic to view details:",
            options=clinics['name'].tolist()
        )
        
        if selected_clinic_name:
            clinic = clinics[clinics['name'] == selected_clinic_name].iloc[0]
            
            # Show map for individual clinic
            if pd.notna(clinic['latitude']) and pd.notna(clinic['longitude']):
                st.markdown("#### 📍 Clinic Location")
                clinic_df = pd.DataFrame([clinic])
                single_clinic_map = create_clinic_map(clinic_df, zoom_start=15)
                st_folium(single_clinic_map, width=None, height=300)
                st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📍 Contact Information**")
                st.write(f"Address: {clinic['address']}")
                st.write(f"Phone: {clinic['phone']}")
                st.write(f"Email: {clinic['email']}")
                st.write(f"Rating: ⭐ {clinic['rating']:.1f}")
                st.write(f"Coordinates: {clinic['latitude']:.6f}, {clinic['longitude']:.6f}")
                
                st.markdown("**🏥 Care Types**")
                st.write(clinic['care_types'])
            
            with col2:
                st.markdown("**💉 Services Offered**")
                if clinic['services']:
                    for svc in clinic['services'].split(','):
                        st.write(f"• {svc}")
                else:
                    st.write("*Not specified*")
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("**🔬 Equipment Available**")
                if clinic['equipment']:
                    for eq in clinic['equipment'].split(','):
                        st.write(f"• {eq}")
                else:
                    st.write("*Not specified*")
            
            with col4:
                st.markdown("**🧪 Laboratory Tests**")
                if clinic['lab_tests']:
                    for lab in clinic['lab_tests'].split(','):
                        st.write(f"• {lab}")
                else:
                    st.write("*Not specified*")
        
        # Statistics
        st.markdown("---")
        st.subheader("📈 Platform Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clinics", len(clinics))
        
        with col2:
            st.metric("Average Rating", f"{clinics['rating'].mean():.2f}")
        
        with col3:
            emergency_count = clinics['emergency_available'].sum()
            st.metric("🚨 Emergency Clinics", int(emergency_count))
        
        with col4:
            inpatient_count = clinics.get('inpatient_care', pd.Series([0])).sum()
            st.metric("🏨 Inpatient Care", int(inpatient_count))
    else:
        st.info("No clinics registered yet. Add your first clinic!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Sofia Vet Platform - Find the best veterinary care for your pet. "
    "Search clinics by services, location, and ratings."
)
