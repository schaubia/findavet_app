"""Recommendation API endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Vet, Review
from app.ml.recommender import VetRecommendationEngine

router = APIRouter()

@router.post("")
async def get_vet_recommendations(
    user_lat: float = Query(..., description="User latitude"),
    user_lon: float = Query(..., description="User longitude"),
    conditions: Optional[str] = None,
    equipment: Optional[str] = None,
    hotel_cats: Optional[bool] = None,
    hotel_dogs: Optional[bool] = None,
    grooming: Optional[bool] = None,
    surgery: Optional[bool] = None,
    vaccination: Optional[bool] = None,
    dental_care: Optional[bool] = None,
    preferred_price: Optional[str] = None,
    needs_emergency: bool = False,
    max_distance_km: float = 50,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """Get personalized vet recommendations"""
    
    required_services = []
    
    if conditions:
        required_services.append({'condition': conditions})
    
    if equipment:
        required_services.append({'equipment': equipment})
    
    boolean_services = {
        'hotel_cats': hotel_cats,
        'hotel_dogs': hotel_dogs,
        'grooming': grooming,
        'surgery': surgery,
        'vaccination': vaccination,
        'dental_care': dental_care
    }
    
    for service_name, service_value in boolean_services.items():
        if service_value:
            required_services.append({service_name: True})
    
    recommender = VetRecommendationEngine(db)
    user_location = {'lat': user_lat, 'lon': user_lon}
    
    recommendations = recommender.get_recommendations(
        user_location=user_location,
        required_services=required_services if required_services else None,
        preferred_price=preferred_price,
        needs_emergency=needs_emergency,
        max_distance_km=max_distance_km,
        top_n=top_n
    )
    
    return recommendations

@router.get("/{vet_id}/similar")
async def get_similar_vets(
    vet_id: int,
    top_n: int = 3,
    db: Session = Depends(get_db)
):
    """Find vets similar to the specified vet"""
    
    recommender = VetRecommendationEngine(db)
    similar_vets = recommender.get_similar_vets(vet_id, top_n)
    
    return similar_vets

@router.get("/popular")
async def get_popular_vets(
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """Get most popular vets based on ratings and review count"""
    
    vets = db.query(Vet).all()
    
    popular_vets = []
    for vet in vets:
        review_count = db.query(Review).filter(Review.vet_id == vet.id).count()
        popularity_score = (vet.rating * 0.7) + (min(review_count / 10, 1.0) * 0.3) * 5
        
        popular_vets.append({
            'vet_id': vet.id,
            'name': vet.name,
            'rating': vet.rating,
            'review_count': review_count,
            'popularity_score': round(popularity_score, 2),
            'phone': vet.phone,
            'address': vet.address,
            'price_range': vet.price_range,
            'emergency_service': vet.emergency_service
        })
    
    popular_vets.sort(key=lambda x: x['popularity_score'], reverse=True)
    
    return {'top_popular_vets': popular_vets[:top_n]}

@router.get("/nearby")
async def get_nearby_vets(
    user_lat: float,
    user_lon: float,
    radius_km: float = 10,
    db: Session = Depends(get_db)
):
    """Get all vets within a specific radius"""
    
    recommender = VetRecommendationEngine(db)
    user_location = {'lat': user_lat, 'lon': user_lon}
    
    all_vets = db.query(Vet).all()
    nearby_vets = []
    
    for vet in all_vets:
        distance = recommender.calculate_distance(
            user_lat, user_lon,
            vet.location_lat, vet.location_lon
        )
        
        if distance <= radius_km:
            nearby_vets.append({
                'vet_id': vet.id,
                'name': vet.name,
                'distance_km': round(distance, 2),
                'rating': vet.rating,
                'phone': vet.phone,
                'address': vet.address,
                'price_range': vet.price_range,
                'location': {'lat': vet.location_lat, 'lon': vet.location_lon}
            })
    
    nearby_vets.sort(key=lambda x: x['distance_km'])
    
    return {
        'user_location': user_location,
        'radius_km': radius_km,
        'found': len(nearby_vets),
        'nearby_vets': nearby_vets
    }