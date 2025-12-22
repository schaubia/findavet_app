# Sofia Vet Platform 🐱

A comprehensive veterinary clinic management and recommendation system built with FastAPI, SQLAlchemy, and machine learning.

## Features

- 🏥 **Clinic Management**: Register and manage veterinary clinics
- 🔍 **Smart Search**: Find vets by services, location, and preferences
- 🤖 **AI Recommendations**: ML-powered vet recommendations based on:
  - Distance and location
  - Service matching
  - Ratings and reviews
  - Price preferences
  - Emergency availability
- ⭐ **Reviews & Ratings**: User reviews and ratings system
- 📅 **Working Hours**: Manage clinic schedules
- 📊 **Analytics**: Visualize recommendation scores

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: SQLite with SQLAlchemy ORM
- **ML**: scikit-learn, geopy for location-based recommendations
- **API Docs**: Interactive Swagger UI

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sofia-vet-platform.git
cd sofia-vet-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Project Structure

```
sofia-vet-platform/
├── app/
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database configuration
│   ├── api/
│   │   ├── vets.py        # Vet endpoints
│   │   └── recommendations.py  # Recommendation endpoints
│   └── ml/
│       └── recommender.py # ML recommendation engine
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
└── README.md
```

## License

MIT License - see LICENSE file for details