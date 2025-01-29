# app/utils/database.py
import os
from mongoengine import connect, disconnect
from dotenv import load_dotenv
from app.utils.config import get_settings
import certifi

settings = get_settings()

def init_db():
    """Initialize database connection"""
    load_dotenv()
    
    # Get MongoDB connection details from environment variables
    MONGODB_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017/migo")
    
    # Disconnect any existing connections
    disconnect()
    
    # Connect to MongoDB
    connect(host=MONGODB_URI, tlsCAFile=certifi.where())

def close_db():
    """Close database connection"""
    disconnect()

def init_db_with_settings():
    connect(
        db=settings.DATABASE_NAME,
        host=settings.MONGODB_URL,
        tlsCAFile=certifi.where()
    ) 
