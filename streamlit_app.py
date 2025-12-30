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

# Translation dictionary
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
        
        # About
        'about': 'About',
        'about_text': 'Sofia Vet Platform - Find the best veterinary care for your pet. Search clinics by services, location, and ratings.',
    },
    'bg': {
        # Page titles
        'app_title': 'София Вет Платформа',
        'app_subtitle': 'Намерете най-добрата ветеринарна клиника за вашия любимец',
        'navigation': 'Навигация',
        'search_clinics': 'Търсене на клиники',
        'add_clinic': 'Добави клиника',
        'add_review': 'Добави отзив',
        'view_all_clinics': 'Всички клиники',
        
        # Search page
        'search_header': 'Търсене на ветеринарни клиники',
        'your_location': 'Вашето местоположение (по избор)',
        'location_help': 'Въведете вашето местоположение, за да намерите най-близките клиники и да видите разстоянията',
        'your_latitude': 'Вашата географскаширина',
        'your_longitude': 'Вашата географска дължина',
        'max_distance': 'Макс. разстояние (км)',
        'search_by_location': 'Търсене по местоположение (намери най-близки клиники)',
        'search_filters': 'Филтри за търсене',
        'quick_searches': 'Бързо търсене (Кликнете за автоматично попълване)',
        'common_searches': 'Често търсени:',
        'hotels_btn': 'Хотели',
        'vaccination_btn': 'Ваксинация',
        'diagnostics_btn': 'Диагностика',
        'emergency_btn': 'Спешни',
        'services': 'Услуги',
        'equipment': 'Оборудване',
        'available': 'налични',
        'select_services': 'Изберете услуги (оставете празно за всички)',
        'select_equipment': 'Изберете оборудване (оставете празно за всички)',
        'service_help': 'Изберете една или повече услуги, които търсите',
        'equipment_help': 'Изберете оборудването, което клиниката трябва да има',
        'emergency_care': 'Спешна помощ',
        'inpatient_care': 'Болнична грижа',
        'wild_animal_care': 'Грижа за диви животни',
        'minimum_rating': 'Минимална оценка',
        'search_btn': 'Търси',
        'clear_btn': 'Изчисти',
        'found_clinics': 'Намерени {count} клиники',
        'active_filters': 'Активни филтри:',
        'rating_filter': 'Оценка',
        'clinic_locations': 'Местоположения на клиники',
        'clinic_details': 'Детайли за клиниките',
        'no_clinics_found': 'Не са намерени клиники, отговарящи на критериите',
        'adjust_filters': 'Опитайте да промените филтрите за търсене или да увеличите радиуса на търсене.',
        'use_search_filters': 'Използвайте филтрите по-горе и натиснете \'Търси\', за да намерите ветеринарни клиники',
        'km_away': '{distance:.2f} км разстояние',
        
        # Clinic details
        'contact_info': 'Информация за контакт',
        'address': 'Адрес',
        'phone': 'Телефон',
        'email': 'Имейл',
        'location': 'Местоположение',
        'coordinates': 'Координати',
        'distance_from_you': 'Разстояние от вас',
        'services_offered': 'Предлагани услуги',
        'equipment_available': 'Налично оборудване',
        'lab_tests': 'Лабораторни изследвания',
        'not_specified': 'Не е посочено',
        'and_more': '...и още {count}',
        'standard_care': 'Стандартна грижа',
        
        # Add clinic page
        'register_clinic': 'Регистрирай нова клиника',
        'basic_info': 'Основна информация',
        'clinic_name': 'Име на клиниката*',
        'clinic_name_placeholder': 'напр., София Пет Кеър',
        'address_placeholder': 'напр., ул. Главна 123, София',
        'phone_placeholder': 'напр., +359 2 123 4567',
        'email_placeholder': 'напр., info@sofiavetcare.com',
        'latitude': 'Географска широчина',
        'longitude': 'Географска дължина',
        'care_types': 'Видове грижи',
        'services_offered_label': 'Предлагани услуги',
        'other_services': 'Други услуги (разделени със запетая)',
        'other_services_placeholder': 'напр., поведенческо обучение, хранителни консултации',
        'equipment_available_label': 'Налично оборудване',
        'other_equipment': 'Друго оборудване (разделено със запетая)',
        'other_equipment_placeholder': 'напр., ЕКГ апарат, апарат за анестезия',
        'lab_tests_label': 'Налични лабораторни изследвания',
        'lab_tests_placeholder': 'Кръвни изследвания\nУринен анализ\nИзследване на фецес\nБиохимичен панел\nРентгенови снимки\nУлтразвукова диагностика',
        
        # Service name translations
        'service_cat_hotel': 'Котешки хотел',
        'service_dog_hotel': 'Кучешки хотел',
        'service_grooming': 'Груминг',
        'service_deworming': 'Обезпаразитяване',
        'service_prophylaxis': 'Профилактика',
        'service_dental_care': 'Дентална грижа',
        'service_surgery': 'Хирургия',
        'service_vaccination': 'Ваксинация',
        'service_ophthalmology': 'Офталмология',
        'service_microchipping': 'Чипиране',
        'service_travel_documents': 'Пътни документи',
        
        # Equipment name translations
        'equipment_xray': 'Рентген',
        'equipment_ultrasound': 'Ултразвук',
        'equipment_incubator': 'Инкубатор',
        'equipment_oxygen': 'Кислородна машина',
        
        # Additional translations
        'register_btn': 'Регистрирай клиника',
        'clinic_registered': 'Клиниката \'{name}\' е регистрирана успешно!',
        'added_items': 'Добавени {services} услуги, {equipment} единици оборудване и {tests} лабораторни изследвания.',
        'fill_required': 'Моля, попълнете всички задължителни полета (означени с *)',
        'registration_error': 'Грешка при регистрация на клиника: {error}',
        'check_db': 'Моля, проверете дали базата данни има правилната структура. Опитайте да изтриете vet_platform.db и рестартирайте приложението.',
        
        # Review page
        'add_review_header': 'Добави отзив',
        'select_clinic': 'Изберете клиника',
        'rating': 'Оценка',
        'your_review': 'Вашият отзив',
        'review_placeholder': 'Споделете вашия опит...',
        'submit_review': 'Изпрати отзив',
        'review_submitted': 'Отзивът е изпратен успешно!',
        'no_clinics_yet': 'Все още няма налични клиники. Моля, първо добавете клиника.',
        
        # View all page
        'all_clinics_header': 'Всички регистрирани клиники',
        'clinics_list': 'Списък на клиниките',
        'clinic_name_col': 'Име на клиниката',
        'address_col': 'Адрес',
        'phone_col': 'Телефон',
        'rating_col': 'Оценка',
        'care_types_col': 'Налични видове грижи',
        'detailed_info': 'Подробна информация за клиниката',
        'select_clinic_details': 'Изберете клиника за детайли:',
        'clinic_location': 'Местоположение на клиниката',
        'platform_stats': 'Статистики на платформата',
        'total_clinics': 'Общо клиники',
        'average_rating': 'Средна оценка',
        'emergency_clinics': 'Спешни клиники',
        'inpatient_clinics': 'Болнична грижа',
        'no_clinics_registered': 'Все още няма регистрирани клиники. Добавете първата си клиника!',
        
        # About
        'about': 'За нас',
        'about_text': 'София Вет Платформа - Намерете най-добрата ветеринарна грижа за вашия любимец. Търсете клиники по услуги, местоположение и оценки.',
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
    # Create a mapping of English names to translation keys
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
    
    # Get translation key
    key = service_map.get(english_name)
    
    # Return translated name if found, otherwise return original
    if key:
        return t(key, lang)
    else:
        return english_name  # Return original if not in map

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

st.sidebar.markdown("---")

# Get current language
lang = st.session_state.language

# Title
st.title(f"🐱 {t('app_title', lang)}")
st.markdown(f"### {t('app_subtitle', lang)}")

# Sidebar for navigation
st.sidebar.title(t('navigation', lang))
page = st.sidebar.radio(
    t('navigation', lang), 
    [t('search_clinics', lang), t('add_clinic', lang), t('add_review', lang), t('view_all_clinics', lang)],
    label_visibility="collapsed"
)

# Search Clinics Page
if page == t('search_clinics', lang):
    st.header(f"🔍 {t('search_header', lang)}")
    
    # Initialize session state for search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_user_location' not in st.session_state:
        st.session_state.search_user_location = None
    
    # Location input section
    st.subheader(f"📍 {t('your_location', lang)}")
    st.markdown(f"*{t('location_help', lang)}*")
    
    col_loc1, col_loc2, col_loc3 = st.columns([2, 2, 1])
    
    with col_loc1:
        user_lat = st.number_input(t('your_latitude', lang), value=42.6977, format="%.6f", help="Sofia center: 42.6977")
    
    with col_loc2:
        user_lon = st.number_input(t('your_longitude', lang), value=23.3219, format="%.6f", help="Sofia center: 23.3219")
    
    with col_loc3:
        max_distance = st.number_input(t('max_distance', lang), value=50.0, min_value=1.0, max_value=200.0, step=5.0)
    
    use_location = st.checkbox(f"🎯 {t('search_by_location', lang)}", value=False)
    
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
    with st.expander(f"⚡ {t('quick_searches', lang)}", expanded=False):
        st.markdown(f"**{t('common_searches', lang)}**")
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        
        with col_q1:
            if st.button(f"🏨 {t('hotels_btn', lang)}", use_container_width=True):
                st.session_state.quick_search_services = ["Cat Hotel", "Dog Hotel"]
        with col_q2:
            if st.button(f"💉 {t('vaccination_btn', lang)}", use_container_width=True):
                st.session_state.quick_search_services = ["Vaccination"]
        with col_q3:
            if st.button(f"🔬 {t('diagnostics_btn', lang)}", use_container_width=True):
                st.session_state.quick_search_equipment = ["X-Ray", "Ultrasound"]
        with col_q4:
            if st.button(f"🚨 {t('emergency_btn', lang)}", use_container_width=True):
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
        st.markdown(f"**💉 {t('services', lang)}** ({len(service_options)} {t('available', lang)})")
        if len(service_options) > 0:
            # Create translated options for display
            service_options_translated = [translate_service_name(s, lang) for s in service_options]
            
            # Create mapping for reverse lookup (translated name -> English name)
            service_display_to_english = {
                translate_service_name(s, lang): s 
                for s in service_options
            }
            
            # Use quick search if available (translate defaults)
            default_services_english = [s for s in st.session_state.quick_search_services if s in service_options]
            default_services_translated = [translate_service_name(s, lang) for s in default_services_english]
            
            selected_services_display = st.multiselect(
                t('select_services', lang),
                options=service_options_translated,
                default=default_services_translated,
                help=t('service_help', lang)
            )
            
            # Convert displayed names back to English for database query
            selected_services = [
                service_display_to_english[s] 
                for s in selected_services_display
            ]
            
            # Clear quick search after use
            if default_services_english:
                st.session_state.quick_search_services = []
        else:
            st.warning("No services registered yet. Add clinics with services first.")
            selected_services = []
    
    with col2:
        st.markdown(f"**🔬 {t('equipment', lang)}** ({len(equipment_options)} {t('available', lang)})")
        if len(equipment_options) > 0:
            # Create translated options for display
            equipment_options_translated = [translate_equipment_name(e, lang) for e in equipment_options]
            
            # Create mapping for reverse lookup
            equipment_display_to_english = {
                translate_equipment_name(e, lang): e 
                for e in equipment_options
            }
            
            # Use quick search if available (translate defaults)
            default_equipment_english = [e for e in st.session_state.quick_search_equipment if e in equipment_options]
            default_equipment_translated = [translate_equipment_name(e, lang) for e in default_equipment_english]
            
            selected_equipment_display = st.multiselect(
                t('select_equipment', lang),
                options=equipment_options_translated,
                default=default_equipment_translated,
                help=t('equipment_help', lang)
            )
            
            # Convert displayed names back to English for database query
            selected_equipment = [
                equipment_display_to_english[e] 
                for e in selected_equipment_display
            ]
            
            # Clear quick search after use
            if default_equipment_english:
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
                        st.markdown(f"#### 💉 {t('services', lang)}")
                        if clinic['services']:
                            services_list = clinic['services'].split(',')
                            for svc in services_list[:5]:  # Show first 5
                                translated_svc = translate_service_name(svc.strip(), lang)
                                st.write(f"• {translated_svc}")
                            if len(services_list) > 5:
                                st.write(f"*{t('and_more', lang, count=len(services_list) - 5)}*")
                        else:
                            st.write(f"*{t('not_specified', lang)}*")
                    
                    with col2:
                        st.markdown(f"#### 🔬 {t('equipment', lang)}")
                        if clinic['equipment']:
                            equip_list = clinic['equipment'].split(',')
                            for eq in equip_list:
                                translated_eq = translate_equipment_name(eq.strip(), lang)
                                st.write(f"• {translated_eq}")
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
        st.subheader(f"💉 {t('services_offered_label', lang)}")
        
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
        
        # Other services input
        other_services = st.text_input(
            f"➕ {t('other_services', lang)}", 
            placeholder=t('other_services_placeholder', lang)
        )
        
        st.markdown("---")
        
        # Equipment
        st.subheader(f"🔬 {t('equipment_available_label', lang)}")
        
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
