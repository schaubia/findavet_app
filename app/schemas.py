"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: str
    phone: str = Field(..., min_length=10, max_length=50)
    address: str = Field(..., min_length=5, max_length=500)
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    price_range: str
    description: Optional[str] = Field(None, max_length=2000)
    website: Optional[str] = None
    emergency_service: bool = False

class VetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=50)
    address: Optional[str] = None
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)
    price_range: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    emergency_service: Optional[bool] = None

class ServiceCreate(BaseModel):
    condition: Optional[str] = Field(None, max_length=255)
    equipment: Optional[str] = Field(None, max_length=255)
    hotel_cats: bool = False
    hotel_dogs: bool = False
    grooming: bool = False
    wild_animals: bool = False
    special_food: Optional[str] = None
    surgery: bool = False
    vaccination: bool = False
    dental_care: bool = False

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=10, max_length=2000)
    reviewer_name: str = Field(..., min_length=2, max_length=255)

class WorkingHoursCreate(BaseModel):
    day_of_week: str
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    is_closed: bool = False

class VetResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str
    location_lat: float
    location_lon: float
    price_range: str
    rating: float
    description: Optional[str]
    website: Optional[str]
    emergency_service: bool
    created_at: datetime
    
    class Config:
        from_attributes = True