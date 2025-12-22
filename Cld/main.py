#!/usr/bin/env python3
"""
Sofia Vet Platform - Main Application Entry Point
"""
import uvicorn
from app.api import create_app

def main():
    """Run the FastAPI application"""
    app = create_app()
    
    print("🐱 Sofia Vet Platform Starting...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📖 Alternative docs: http://localhost:8000/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()