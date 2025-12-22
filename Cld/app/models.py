"""SQLAlchemy database models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Vet(Base):
    __tablename__ = "vets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    address = Column(String(500))
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    price_range = Column(String(50))
    rating = Column(Float, default=0.0)
    description = Column(Text)
    website = Column(String(255))
    emergency_service = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    services = relationship("Service", back_populates="vet", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="vet", cascade="all, delete-orphan")
    working_hours = relationship("WorkingHours", back_populates="vet", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    vet_id = Column(Integer, ForeignKey("vets.id", ondelete="CASCADE"), nullable=False)
    condition = Column(String(255))
    equipment = Column(String(255))
    hotel_cats = Column(Boolean, default=False)
    hotel_dogs = Column(Boolean, default=False)
    grooming = Column(Boolean, default=False)
    wild_animals = Column(Boolean, default=False)
    special_food = Column(String(255), nullable=True)
    surgery = Column(Boolean, default=False)
    vaccination = Column(Boolean, default=False)
    dental_care = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vet = relationship("Vet", back_populates="services")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    vet_id = Column(Integer, ForeignKey("vets.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text)
    reviewer_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vet = relationship("Vet", back_populates="reviews")

class WorkingHours(Base):
    __tablename__ = "working_hours"
    
    id = Column(Integer, primary_key=True, index=True)
    vet_id = Column(Integer, ForeignKey("vets.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    open_time = Column(String(10))
    close_time = Column(String(10))
    is_closed = Column(Boolean, default=False)
    
    vet = relationship("Vet", back_populates="working_hours")