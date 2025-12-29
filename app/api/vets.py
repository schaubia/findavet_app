"""Vet management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime

from app.database import get_db
from app.models import Vet, Service, Review, WorkingHours
from app.schemas import (
    VetCreate, VetUpdate, VetResponse,
    ServiceCreate, ReviewCreate, WorkingHoursCreate
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_vet(vet_data: VetCreate, db: Session = Depends(get_db)):
    """Register a new veterinary clinic"""
    existing_vet = db.query(Vet).filter(Vet.email == vet_data.email).first()
    if existing_vet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vet with email {vet_data.email} already registered"
        )
    
    try:
        new_vet = Vet(
            name=vet_data.name,
            email=vet_data.email,
            phone=vet_data.phone,
            address=vet_data.address,
            location_lat=vet_data.location_lat,
            location_lon=vet_data.location_lon,
            price_range=vet_data.price_range,
            description=vet_data.description,
            website=vet_data.website,
            emergency_service=vet_data.emergency_service,
            rating=0.0
        )
        
        db.add(new_vet)
        db.commit()
        db.refresh(new_vet)
        
        logger.info(f"New vet registered: {new_vet.name} (ID: {new_vet.id})")
        return new_vet
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering vet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@router.get("/{vet_id}")
async def get_vet(vet_id: int, db: Session = Depends(get_db)):
    """Get a specific vet by ID"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    return vet

@router.put("/{vet_id}")
async def update_vet(vet_id: int, vet_data: VetUpdate, db: Session = Depends(get_db)):
    """Update veterinary clinic information"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    try:
        update_data = vet_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vet, field, value)
        
        vet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vet)
        
        logger.info(f"Vet updated: {vet.name} (ID: {vet.id})")
        return vet
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating vet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{vet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vet(vet_id: int, db: Session = Depends(get_db)):
    """Delete a veterinary clinic"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    try:
        db.delete(vet)
        db.commit()
        logger.info(f"Vet deleted: ID {vet_id}")
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{vet_id}/services", status_code=status.HTTP_201_CREATED)
async def add_service(vet_id: int, service_data: ServiceCreate, db: Session = Depends(get_db)):
    """Add services offered by a veterinary clinic"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    try:
        new_service = Service(
            vet_id=vet_id,
            condition=service_data.condition,
            equipment=service_data.equipment,
            hotel_cats=service_data.hotel_cats,
            hotel_dogs=service_data.hotel_dogs,
            grooming=service_data.grooming,
            wild_animals=service_data.wild_animals,
            special_food=service_data.special_food,
            surgery=service_data.surgery,
            vaccination=service_data.vaccination,
            dental_care=service_data.dental_care
        )
        
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        
        return {
            "success": True,
            "service_id": new_service.id,
            "vet_name": vet.name,
            "message": "Service added successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vet_id}/services")
async def get_vet_services(vet_id: int, db: Session = Depends(get_db)):
    """Get all services offered by a specific vet"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    services = db.query(Service).filter(Service.vet_id == vet_id).all()
    return {"vet_name": vet.name, "services": services}

@router.post("/{vet_id}/working-hours", status_code=status.HTTP_201_CREATED)
async def add_working_hours(vet_id: int, hours_data: WorkingHoursCreate, db: Session = Depends(get_db)):
    """Add working hours for a specific day"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    existing = db.query(WorkingHours).filter(
        WorkingHours.vet_id == vet_id,
        WorkingHours.day_of_week == hours_data.day_of_week
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Working hours for {hours_data.day_of_week} already exist"
        )
    
    try:
        new_hours = WorkingHours(
            vet_id=vet_id,
            day_of_week=hours_data.day_of_week,
            open_time=hours_data.open_time,
            close_time=hours_data.close_time,
            is_closed=hours_data.is_closed
        )
        
        db.add(new_hours)
        db.commit()
        db.refresh(new_hours)
        
        return {"success": True, "working_hours_id": new_hours.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vet_id}/working-hours")
async def get_working_hours(vet_id: int, db: Session = Depends(get_db)):
    """Get all working hours for a vet"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    hours = db.query(WorkingHours).filter(WorkingHours.vet_id == vet_id).all()
    return {"vet_name": vet.name, "working_hours": hours}

@router.get("")
async def list_vets(
    skip: int = 0,
    limit: int = 100,
    price_range: Optional[str] = None,
    emergency_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all veterinary clinics with optional filters"""
    query = db.query(Vet)
    
    if price_range:
        query = query.filter(Vet.price_range == price_range)
    
    if emergency_only:
        query = query.filter(Vet.emergency_service == True)
    
    vets = query.offset(skip).limit(limit).all()
    
    return {
        "total": len(vets),
        "vets": [
            {
                "id": v.id,
                "name": v.name,
                "phone": v.phone,
                "address": v.address,
                "rating": v.rating,
                "price_range": v.price_range,
                "emergency_service": v.emergency_service,
                "location": {"lat": v.location_lat, "lon": v.location_lon}
            }
            for v in vets
        ]
    }

@router.post("/{vet_id}/reviews", status_code=status.HTTP_201_CREATED)
async def add_review(vet_id: int, review_data: ReviewCreate, db: Session = Depends(get_db)):
    """Add a review for a vet"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    try:
        new_review = Review(
            vet_id=vet_id,
            rating=review_data.rating,
            text=review_data.text,
            reviewer_name=review_data.reviewer_name
        )
        
        db.add(new_review)
        
        all_reviews = db.query(Review).filter(Review.vet_id == vet_id).all()
        total_rating = sum(r.rating for r in all_reviews) + review_data.rating
        vet.rating = total_rating / (len(all_reviews) + 1)
        
        db.commit()
        db.refresh(new_review)
        
        return {
            "success": True,
            "review_id": new_review.id,
            "new_average_rating": round(vet.rating, 2)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vet_id}/reviews")
async def get_reviews(vet_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a vet"""
    vet = db.query(Vet).filter(Vet.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Vet not found")
    
    reviews = db.query(Review).filter(Review.vet_id == vet_id).order_by(Review.created_at.desc()).all()
    
    return {
        "vet_name": vet.name,
        "average_rating": vet.rating,
        "total_reviews": len(reviews),
        "reviews": reviews
    }