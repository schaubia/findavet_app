"""Intelligent Vet Recommendation System"""
from geopy.distance import geodesic
from sqlalchemy.orm import Session
from app.models import Vet, Service, Review

class VetRecommendationEngine:
    """AI-powered recommendation system for veterinary clinics"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        try:
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        except:
            return float('inf')
    
    def get_service_match_score(self, vet_services: list, required_services: list) -> float:
        """Calculate how well vet services match required services"""
        if not required_services:
            return 1.0
        
        matches = 0
        total = len(required_services)
        
        for service in vet_services:
            for req_service in required_services:
                if req_service.get('condition') and service.condition:
                    if req_service['condition'].lower() in service.condition.lower():
                        matches += 1
                        continue
                
                if req_service.get('equipment') and service.equipment:
                    if req_service['equipment'].lower() in service.equipment.lower():
                        matches += 0.8
                        continue
                
                boolean_services = ['hotel_cats', 'hotel_dogs', 'grooming', 
                                  'wild_animals', 'surgery', 'vaccination', 'dental_care']
                for bool_service in boolean_services:
                    if req_service.get(bool_service) and getattr(service, bool_service, False):
                        matches += 0.5
        
        return min(matches / total, 1.0) if total > 0 else 0.0
    
    def get_price_match_score(self, vet_price_range: str, preferred_price_range: str) -> float:
        """Calculate price preference match"""
        if not preferred_price_range:
            return 1.0
        
        price_map = {'low': 1, 'med': 2, 'high': 3}
        vet_price = price_map.get(vet_price_range, 2)
        pref_price = price_map.get(preferred_price_range, 2)
        
        diff = abs(vet_price - pref_price)
        return 1.0 - (diff * 0.3)
    
    def get_emergency_score(self, vet_emergency: bool, needs_emergency: bool) -> float:
        """Score for emergency service availability"""
        if not needs_emergency:
            return 1.0
        return 1.0 if vet_emergency else 0.0
    
    def calculate_vet_score(
        self,
        vet: Vet,
        user_location: dict,
        required_services: list = None,
        preferred_price: str = None,
        needs_emergency: bool = False,
        max_distance_km: float = 50
    ) -> dict:
        """Calculate comprehensive recommendation score"""
        
        distance = self.calculate_distance(
            user_location['lat'], user_location['lon'],
            vet.location_lat, vet.location_lon
        )
        
        if distance > max_distance_km:
            return None
        
        distance_score = 1.0 - (distance / max_distance_km)
        distance_score = max(0, distance_score)
        
        vet_services = self.db.query(Service).filter(Service.vet_id == vet.id).all()
        service_score = self.get_service_match_score(vet_services, required_services or [])
        
        rating_score = vet.rating / 5.0 if vet.rating else 0.5
        price_score = self.get_price_match_score(vet.price_range, preferred_price)
        emergency_score = self.get_emergency_score(vet.emergency_service, needs_emergency)
        
        total_score = (
            distance_score * 0.30 +
            service_score * 0.30 +
            rating_score * 0.20 +
            price_score * 0.10 +
            emergency_score * 0.10
        )
        
        return {
            'vet_id': vet.id,
            'vet_name': vet.name,
            'total_score': round(total_score * 100, 2),
            'distance_km': round(distance, 2),
            'distance_score': round(distance_score * 100, 2),
            'service_match_score': round(service_score * 100, 2),
            'rating_score': round(rating_score * 100, 2),
            'price_match_score': round(price_score * 100, 2),
            'emergency_score': round(emergency_score * 100, 2),
            'vet_details': {
                'phone': vet.phone,
                'address': vet.address,
                'rating': vet.rating,
                'price_range': vet.price_range,
                'emergency_service': vet.emergency_service,
                'website': vet.website,
                'location': {'lat': vet.location_lat, 'lon': vet.location_lon}
            }
        }
    
    def get_recommendations(
        self,
        user_location: dict,
        required_services: list = None,
        preferred_price: str = None,
        needs_emergency: bool = False,
        max_distance_km: float = 50,
        top_n: int = 5
    ) -> dict:
        """Get top N vet recommendations"""
        
        all_vets = self.db.query(Vet).all()
        
        if not all_vets:
            return {'message': 'No vets found in database', 'recommendations': []}
        
        recommendations = []
        for vet in all_vets:
            score_data = self.calculate_vet_score(
                vet, user_location, required_services,
                preferred_price, needs_emergency, max_distance_km
            )
            
            if score_data:
                recommendations.append(score_data)
        
        recommendations.sort(key=lambda x: x['total_score'], reverse=True)
        
        return {
            'total_found': len(recommendations),
            'showing_top': min(top_n, len(recommendations)),
            'user_location': user_location,
            'filters': {
                'required_services': required_services,
                'preferred_price': preferred_price,
                'needs_emergency': needs_emergency,
                'max_distance_km': max_distance_km
            },
            'recommendations': recommendations[:top_n]
        }
    
    def get_similar_vets(self, vet_id: int, top_n: int = 3) -> dict:
        """Find similar vets based on services"""
        
        target_vet = self.db.query(Vet).filter(Vet.id == vet_id).first()
        if not target_vet:
            return {'error': 'Vet not found'}
        
        all_vets = self.db.query(Vet).filter(Vet.id != vet_id).all()
        target_services = self.db.query(Service).filter(Service.vet_id == vet_id).all()
        
        similarities = []
        for vet in all_vets:
            vet_services = self.db.query(Service).filter(Service.vet_id == vet.id).all()
            
            similarity_score = self.calculate_service_similarity(target_services, vet_services)
            price_similarity = 1.0 if vet.price_range == target_vet.price_range else 0.5
            total_similarity = (similarity_score * 0.7) + (price_similarity * 0.3)
            
            similarities.append({
                'vet_id': vet.id,
                'vet_name': vet.name,
                'similarity_score': round(total_similarity * 100, 2),
                'rating': vet.rating,
                'price_range': vet.price_range,
                'phone': vet.phone,
                'address': vet.address
            })
        
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            'reference_vet': target_vet.name,
            'similar_vets': similarities[:top_n]
        }
    
    def calculate_service_similarity(self, services1: list, services2: list) -> float:
        """Calculate similarity between two sets of services"""
        if not services1 or not services2:
            return 0.0
        
        features = ['hotel_cats', 'hotel_dogs', 'grooming', 'wild_animals', 
                   'surgery', 'vaccination', 'dental_care']
        
        vec1 = [any(getattr(s, f, False) for s in services1) for f in features]
        vec2 = [any(getattr(s, f, False) for s in services2) for f in features]
        
        intersection = sum(a and b for a, b in zip(vec1, vec2))
        union = sum(a or b for a, b in zip(vec1, vec2))
        
        return intersection / union if union > 0 else 0.0