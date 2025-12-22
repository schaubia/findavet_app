"""FastAPI application factory"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import vets, recommendations

def create_app():
    app = FastAPI(
        title="Sofia Vet Platform API",
        description="Complete API for veterinary clinic management",
        version="2.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    init_db()
    
    app.include_router(vets.router, prefix="/vets", tags=["vets"])
    app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
    
    return app