# Sofia Vet Platform - Streamlit Version 🐱

A simple Streamlit web application for finding and managing veterinary clinics.

## Features

* 🔍 **Search Clinics**: Find vets by services, ratings, and emergency availability
* 🏥 **Register Clinics**: Add new veterinary clinics to the platform
* ⭐ **Add Reviews**: Rate and review clinics
* 📊 **View Statistics**: See all registered clinics and platform stats

## Local Development

### 1. Install dependencies

```bash
pip install -r requirements_streamlit.txt
```

### 2. Run the app

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Deploy to Streamlit Cloud

### Option 1: Via GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add streamlit_app.py requirements_streamlit.txt
   git commit -m "Add Streamlit version"
   git push
   ```

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository: `schaubia/findavet_app`
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

### Option 2: Manual Deployment

1. **Create a Streamlit Cloud account** at [share.streamlit.io](https://share.streamlit.io)

2. **Configure your app**:
   - Repository: Your GitHub repo URL
   - Branch: `main`
   - Main file: `streamlit_app.py`

3. **Deploy**: Click the deploy button and wait a few minutes

## File Structure

```
findavet_app/
├── streamlit_app.py          # Main Streamlit application
├── requirements_streamlit.txt # Python dependencies
├── vet_platform.db           # SQLite database (auto-created)
└── README_STREAMLIT.md       # This file
```

## Database

The app uses SQLite and will automatically create a `vet_platform.db` file on first run. The database includes:

- **clinics**: Veterinary clinic information
- **services**: Services offered by each clinic
- **reviews**: User reviews and ratings

## Usage

### Search for Clinics
1. Go to "Search Clinics" page
2. Enter service name, set filters
3. Click "Search"
4. View results with ratings and details

### Register a Clinic
1. Go to "Add Clinic" page
2. Fill in clinic details
3. Add services (one per line)
4. Click "Register Clinic"

### Add a Review
1. Go to "Add Review" page
2. Select a clinic
3. Rate and write your review
4. Click "Submit Review"

## Important Notes

- This is a simplified version that doesn't include the ML recommendation system from the FastAPI version
- The database starts empty - you'll need to add clinics first
- All data is stored in SQLite (portable but not suitable for high-traffic production)
- For production use with the ML features, consider keeping the FastAPI backend

## Support

For issues or questions, please open an issue on GitHub.

## License

This project is provided as-is for educational purposes.
