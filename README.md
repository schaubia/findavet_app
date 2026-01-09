# Sofia Vet Platform 🐱

A comprehensive veterinary clinic discovery platform with AI-powered recommendations and bilingual support (English/Bulgarian).

## 🌟 Features

### 🔍 **Smart Search**
Find veterinary clinics using advanced filtering:
- **Location-based search** with distance calculations
- **Service filtering** (Cat Hotel, Dog Hotel, Grooming, Vaccination, Surgery, etc.)
- **Equipment filtering** (X-Ray, Ultrasound, Incubator, Oxygen Machine)
- **Care type filters** (Emergency, Inpatient, Wild Animal care)
- **Rating-based filtering**
- **Interactive map visualization** with clinic markers

### 🤖 **AI Recommendations** (New!)
Get personalized clinic recommendations powered by machine learning:
- **Weighted scoring algorithm** considers:
  - Distance from your location (30%)
  - Service and equipment matching (30%)
  - Clinic ratings and reviews (20%)
  - Price preferences (10%)
  - Emergency service availability (10%)
- **Detailed score breakdown** for each recommendation
- **Smart ranking** based on your specific needs
- **Visual metrics** showing why each clinic was recommended

### 🏥 **Clinic Management**
- **Easy registration** with comprehensive clinic information
- **Service management** with predefined and custom options
- **Equipment tracking** (medical equipment inventory)
- **Laboratory tests** catalog
- **Care type indicators** (Emergency, Inpatient, Wild Animal)
- **Geolocation support** with coordinates

### ⭐ **Reviews & Price Ratings**
- **Star ratings** (1-5 stars) for clinic quality
- **Price ratings** ($, $$, $$$) to help budget planning
- **Written reviews** to share experiences
- **Average ratings** automatically calculated
- **Review-based filtering** in search

### 📊 **View All Clinics**
- **Interactive map** showing all registered clinics
- **Sortable table** with key information
- **Detailed clinic profiles** with expandable cards
- **Statistics dashboard** (total clinics, average ratings, emergency availability)
- **Price indicators** based on user reviews

### 💾 **Backup & Restore**
- **Database backup** as downloadable JSON files
- **Easy restoration** from backup files
- **Timestamped backups** for version control
- **Data persistence** across app restarts (essential for cloud deployments)

### 🌍 **Bilingual Support**
- **Full English/Bulgarian interface**
- **Seamless language switching**
- **Translated service and equipment names**
- **Localized UI elements**

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web application framework
- **Folium** - Interactive maps with OpenStreetMap
- **Pandas** - Data manipulation and analysis

### Database
- **SQLite** - Lightweight, embedded database
- **SQLAlchemy-compatible** schema for easy migration

### Machine Learning
- **Custom recommendation engine** with weighted scoring
- **Geopy** - Geographic distance calculations
- **Service matching algorithm** for smart filtering

### Languages
- **Python 3.8+**
- **SQL** for database queries

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/schaubia/findavet_app.git
cd findavet_app

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements
```txt
streamlit>=1.28.0
pandas>=2.0.0
folium>=0.14.0
streamlit-folium>=0.15.0
geopy>=2.3.0
```

## 🚀 Running the Application

### Local Development
```bash
# Run the Streamlit app
streamlit run streamlit_app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

### Streamlit Cloud Deployment
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

**Important:** Use the Backup & Restore feature regularly when deployed on Streamlit Cloud, as the database resets when the app sleeps.

## 📖 Usage Guide

### For Users (Finding a Vet)

#### Option 1: Basic Search
1. Go to **"Search Clinics"**
2. Optionally enter your location (lat/lon)
3. Select services and equipment you need
4. Apply filters (emergency, rating, etc.)
5. Click **"Search"**
6. View results on map and in detailed cards

#### Option 2: AI Recommendations
1. Go to **"AI Recommendations"**
2. Enter your location
3. Select your requirements and preferences
4. Set price preference and minimum rating
5. Click **"Get Recommendations"**
6. View ranked results with match scores

### For Clinic Owners (Registering)

1. Go to **"Add Clinic"**
2. Fill in basic information:
   - Name, address, phone, email
   - Coordinates (latitude/longitude)
3. Select care types available
4. Check services offered (or add custom ones)
5. Check equipment available (or add custom items)
6. Add laboratory tests (one per line)
7. Click **"Register Clinic"**

### For Patients (Leaving Reviews)

1. Go to **"Add Review"**
2. Select the clinic you visited
3. Rate quality (1-5 stars)
4. Rate price ($, $$, $$$)
5. Write your experience
6. Submit review

### Data Management

#### Creating Backups
1. Go to **"Backup & Restore"**
2. Click **"Create Backup"**
3. Download the JSON file
4. Store it safely (Google Drive, Dropbox, etc.)

#### Restoring from Backup
1. Go to **"Backup & Restore"**
2. Upload your backup JSON file
3. Click **"Restore from Backup"**
4. All data will be restored

## 🗺️ Database Schema

### Tables
- **clinics** - Main clinic information
- **services** - Services offered by clinics
- **equipment** - Medical equipment available
- **lab_tests** - Laboratory tests offered
- **reviews** - User reviews with ratings and price ratings

### Key Fields
- Clinics: name, address, phone, email, coordinates, rating, care types
- Reviews: rating (1-5), price_rating (1-3), comment
- Services: service_name (predefined + custom)
- Equipment: equipment_name (predefined + custom)

## 🎯 Use Cases

### For Pet Owners
- Find the nearest vet for emergencies
- Compare prices across clinics
- Read reviews before visiting
- Find specialists (e.g., wild animal care)
- Get AI recommendations based on needs

### For Clinic Owners
- List their clinic and services
- Attract new patients
- Showcase specialized equipment
- Build reputation through reviews

### For the Community
- Comprehensive directory of Sofia vets
- Transparent pricing information
- Quality ratings and reviews
- Emergency service availability

## 🌐 Supported Services

- Cat Hotel / Dog Hotel
- Grooming
- Deworming
- Prophylaxis
- Dental Care
- Surgery
- Vaccination
- Ophthalmology
- Microchipping
- Travel Documents
- ...and custom services

## 🔬 Supported Equipment

- X-Ray machines
- Ultrasound devices
- Incubators
- Oxygen machines
- ...and custom equipment

## 🏆 Key Benefits

✅ **User-friendly** - Clean, intuitive interface  
✅ **Bilingual** - English and Bulgarian support  
✅ **Smart** - AI-powered recommendations  
✅ **Comprehensive** - All clinic info in one place  
✅ **Visual** - Interactive maps and charts  
✅ **Reliable** - Backup and restore functionality  
✅ **Mobile-friendly** - Responsive design  
✅ **Open source** - Free to use and modify

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions
- Add more languages (German, French, etc.)
- Integrate appointment booking
- Add clinic photos/galleries
- Implement user accounts
- Add email notifications
- Create mobile app version
- Add payment integration
- Implement clinic availability calendar



## 🙏 Acknowledgments

- OpenStreetMap for map tiles
- Streamlit team for the amazing framework
- Sofia pet owners community for feedback
- All clinic owners who register their services

## 📞 Support

For questions or issues:
- Open an issue on GitHub


## 🔮 Future Enhancements

- [ ] User authentication system
- [ ] Clinic owner dashboard
- [ ] Appointment scheduling
- [ ] SMS/Email notifications
- [ ] Photo uploads for clinics
- [ ] Advanced analytics dashboard
- [ ] Integration with payment systems
- [ ] Mobile app (iOS/Android)
- [ ] API for third-party integrations
- [ ] Multi-city support
- [ ] Veterinarian profiles

---

**Made with ❤️ for Sofia's pets and their owners**

🐱 🐶 🐹 🐰 🐦 🦎
