"""
CRM Database Models for Independent Dealer Prospector
Defines SQLAlchemy models for prospects, communications, searches, and visits.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
from typing import Optional
import os

Base = declarative_base()

class Prospect(Base):
    """Core prospect/dealership model"""
    __tablename__ = 'prospects'
    
    id = Column(Integer, primary_key=True)
    place_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    address = Column(String(1000))
    phone = Column(String(50))
    website = Column(String(500))
    rating = Column(Float)
    total_reviews = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # CRM Status Fields
    status = Column(String(50), default='prospect')  # prospect, contacted, qualified, visited, dnc
    priority = Column(String(20), default='standard')  # high, standard, low
    ai_score = Column(Integer, default=0)  # 0-100 AI scoring
    
    # Contact Information
    contact_person = Column(String(200))
    contact_email = Column(String(200))
    contact_title = Column(String(100))
    
    # Business Information
    business_hours = Column(JSON)  # Store hours as JSON
    categories = Column(JSON)  # Store categories as JSON array
    price_level = Column(Integer)
    
    # Territory & Source
    source_zip = Column(String(10))
    distance_miles = Column(Float)
    
    # Tracking
    first_found_date = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    first_visited_date = Column(DateTime)
    is_visited = Column(Boolean, default=False)
    
    # Notes
    sales_notes = Column(Text)
    
    # Relationships
    communications = relationship("Communication", back_populates="prospect", cascade="all, delete-orphan")
    search_results = relationship("SearchResult", back_populates="prospect")
    
    def __repr__(self):
        return f"<Prospect(name='{self.name}', status='{self.status}')>"

class Communication(Base):
    """Communication log for all prospect interactions"""
    __tablename__ = 'communications'
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    
    # Communication Details
    channel = Column(String(20), nullable=False)  # call, email, sms, visit, note
    direction = Column(String(20), default='outbound')  # outbound, inbound
    status = Column(String(20))  # sent, delivered, failed, answered, no_answer, etc.
    
    # Content
    subject = Column(String(500))
    message = Column(Text)
    response = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    scheduled_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # External IDs (for Twilio, SendGrid, etc.)
    external_id = Column(String(100))
    external_status = Column(String(50))
    
    # Relationships
    prospect = relationship("Prospect", back_populates="communications")
    
    def __repr__(self):
        return f"<Communication(channel='{self.channel}', status='{self.status}')>"

class Search(Base):
    """Search history for territory prospecting"""
    __tablename__ = 'searches'
    
    id = Column(Integer, primary_key=True)
    
    # Search Parameters
    zip_codes = Column(JSON)  # Array of ZIP codes searched
    radius_miles = Column(Integer, default=25)
    min_rating = Column(Float, default=0.0)
    search_terms = Column(JSON)  # Additional search parameters
    
    # Results
    total_found = Column(Integer, default=0)
    new_prospects = Column(Integer, default=0)
    duplicate_prospects = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    search_duration_seconds = Column(Float)
    
    # AI Analysis
    ai_insights = Column(Text)
    territory_analysis = Column(Text)
    
    # Relationships
    search_results = relationship("SearchResult", back_populates="search", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Search(zip_codes={self.zip_codes}, total_found={self.total_found})>"

class SearchResult(Base):
    """Junction table linking searches to prospects found"""
    __tablename__ = 'search_results'
    
    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey('searches.id'), nullable=False)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    
    # Result-specific data
    distance_from_search = Column(Float)
    ai_score_at_time = Column(Integer)
    was_new_prospect = Column(Boolean, default=True)
    
    # Relationships
    search = relationship("Search", back_populates="search_results")
    prospect = relationship("Prospect", back_populates="search_results")

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: Optional[str] = None):
        if database_url is None:
            # Default to environment variable or SQLite fallback
            database_url = os.getenv('DATABASE_URL', 'sqlite:///crm_data.db')
        
        # Handle SQLite path resolution
        if database_url.startswith('sqlite:///') and not database_url.startswith('sqlite:////'):
            # Relative path - make it absolute to current working directory
            db_path = database_url.replace('sqlite:///', '')
            database_url = f'sqlite:///{os.path.abspath(db_path)}'
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
        
    def close(self):
        """Close the database connection"""
        self.engine.dispose()

# Global database manager instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create global database manager"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
        db_manager.create_tables()
    return db_manager

def get_db_session():
    """Get a database session"""
    return get_db_manager().get_session() 