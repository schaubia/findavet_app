import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

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
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinic_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (clinic_id) REFERENCES clinics (id)
        )
    """)
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_service = st.text_input("Search by service (e.g., vaccination, surgery)")
    
    with col2:
        emergency_only = st.checkbox("Emergency available only")
    
    min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, 0.5)
    
    if st.button("Search"):
        conn = get_db_connection()
        query = """
            SELECT DISTINCT c.*, 
                   GROUP_CONCAT(DISTINCT s.service_name) as services
            FROM clinics c
            LEFT JOIN services s ON c.id = s.clinic_id
            WHERE 1=1
        """
        params = []
        
        if search_service:
            query += " AND s.service_name LIKE ?"
            params.append(f"%{search_service}%")
        
        if emergency_only:
            query += " AND c.emergency_available = 1"
        
        query += " AND c.rating >= ?"
        params.append(min_rating)
        
        query += " GROUP BY c.id ORDER BY c.rating DESC"
        
        results = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if len(results) > 0:
            st.success(f"Found {len(results)} clinic(s)")
            
            for _, clinic in results.iterrows():
                with st.expander(f"⭐ {clinic['name']} - Rating: {clinic['rating']:.1f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Address:** {clinic['address']}")
                        st.write(f"**Phone:** {clinic['phone']}")
                        st.write(f"**Email:** {clinic['email']}")
                    
                    with col2:
                        st.write(f"**Services:** {clinic['services'] if clinic['services'] else 'N/A'}")
                        st.write(f"**Emergency:** {'✅ Yes' if clinic['emergency_available'] else '❌ No'}")
        else:
            st.warning("No clinics found matching your criteria")

# Add Clinic Page
elif page == "Add Clinic":
    st.header("🏥 Register New Clinic")
    
    with st.form("add_clinic_form"):
        name = st.text_input("Clinic Name*", placeholder="e.g., Sofia Pet Care")
        address = st.text_input("Address*", placeholder="e.g., 123 Main St, Sofia")
        phone = st.text_input("Phone", placeholder="e.g., +359 2 123 4567")
        email = st.text_input("Email", placeholder="e.g., info@sofiavetcare.com")
        
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=42.6977, format="%.6f")
        with col2:
            longitude = st.number_input("Longitude", value=23.3219, format="%.6f")
        
        emergency = st.checkbox("Emergency services available")
        
        services = st.text_area("Services (one per line)", 
                               placeholder="vaccination\nsurgery\ndental care\ngrooming")
        
        submitted = st.form_submit_button("Register Clinic")
        
        if submitted:
            if name and address:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Convert boolean to integer for SQLite
                    emergency_int = 1 if emergency else 0
                    
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
                    
                    # Insert clinic
                    placeholders = ', '.join(['?'] * len(insert_vals))
                    cols_str = ', '.join(insert_cols)
                    
                    cursor.execute(f"""
                        INSERT INTO clinics ({cols_str})
                        VALUES ({placeholders})
                    """, tuple(insert_vals))
                    
                    clinic_id = cursor.lastrowid
                
                    # Insert services
                    if services:
                        service_list = [s.strip() for s in services.split('\n') if s.strip()]
                        for service in service_list:
                            cursor.execute("""
                                INSERT INTO services (clinic_id, service_name)
                                VALUES (?, ?)
                            """, (clinic_id, service))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Clinic '{name}' registered successfully!")
                    
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
               GROUP_CONCAT(DISTINCT s.service_name) as services
        FROM clinics c
        LEFT JOIN reviews r ON c.id = r.id
        LEFT JOIN services s ON c.id = s.clinic_id
        GROUP BY c.id
        ORDER BY c.rating DESC, c.name
    """, conn)
    conn.close()
    
    if len(clinics) > 0:
        st.dataframe(
            clinics[['name', 'address', 'phone', 'rating', 'emergency_available', 'services']], 
            use_container_width=True,
            hide_index=True
        )
        
        # Statistics
        st.subheader("📈 Platform Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Clinics", len(clinics))
        
        with col2:
            st.metric("Average Rating", f"{clinics['rating'].mean():.2f}")
        
        with col3:
            emergency_count = clinics['emergency_available'].sum()
            st.metric("Emergency Clinics", int(emergency_count))
    else:
        st.info("No clinics registered yet. Add your first clinic!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Sofia Vet Platform - Find the best veterinary care for your pet. "
    "Search clinics by services, location, and ratings."
)