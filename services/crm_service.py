"""
CRM Service Layer for Independent Dealer Prospector
Handles all prospect CRUD operations, status management, and data persistence.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
import logging

from models.database import get_db_session, Prospect, Communication, Search, SearchResult

logger = logging.getLogger(__name__)

def _get_prospect_value(prospect_data, key, default=None):
    """Helper function to safely get values from prospect (dict or SQLAlchemy object)"""
    if hasattr(prospect_data, key):
        value = getattr(prospect_data, key)
        return value if value is not None else default
    elif isinstance(prospect_data, dict):
        return prospect_data.get(key, default)
    else:
        return default

class CRMService:
    """Service layer for CRM operations"""
    
    def __init__(self):
        self.session = None
    
    def _get_session(self) -> Session:
        """Get database session"""
        if self.session is None:
            self.session = get_db_session()
        return self.session
    
    def close_session(self):
        """Close database session"""
        if self.session:
            self.session.close()
            self.session = None
    
    # PROSPECT OPERATIONS
    
    def save_prospect(self, prospect_data) -> Prospect:
        """Save or update a prospect in the database"""
        session = self._get_session()
        
        try:
            # Check if prospect already exists by place_id
            place_id = _get_prospect_value(prospect_data, 'place_id')
            existing = session.query(Prospect).filter(
                Prospect.place_id == place_id
            ).first()
            
            if existing:
                # Update existing prospect
                if isinstance(prospect_data, dict):
                    for key, value in prospect_data.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                existing.last_updated = datetime.now()
                prospect = existing
            else:
                # Create new prospect
                if isinstance(prospect_data, dict):
                    prospect = Prospect(**prospect_data)
                else:
                    # If it's already a Prospect object, use it
                    prospect = prospect_data
                session.add(prospect)
            
            session.commit()
            session.refresh(prospect)
            return prospect
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving prospect: {e}")
            raise
    
    def get_prospect_by_place_id(self, place_id: str) -> Optional[Prospect]:
        """Get prospect by Google Place ID"""
        session = self._get_session()
        return session.query(Prospect).filter(Prospect.place_id == place_id).first()
    
    def get_prospect_by_id(self, prospect_id: int) -> Optional[Prospect]:
        """Get prospect by internal ID"""
        session = self._get_session()
        return session.query(Prospect).filter(Prospect.id == prospect_id).first()
    
    def get_all_prospects(self, 
                         status: Optional[str] = None,
                         priority: Optional[str] = None,
                         visited: Optional[bool] = None,
                         limit: Optional[int] = None) -> List[Prospect]:
        """Get prospects with optional filtering"""
        session = self._get_session()
        query = session.query(Prospect)
        
        if status:
            query = query.filter(Prospect.status == status)
        if priority:
            query = query.filter(Prospect.priority == priority)
        if visited is not None:
            query = query.filter(Prospect.is_visited == visited)
        
        query = query.order_by(desc(Prospect.ai_score), desc(Prospect.last_updated))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_prospect_status(self, prospect_id: int, status: str) -> bool:
        """Update prospect status"""
        session = self._get_session()
        
        try:
            prospect = session.query(Prospect).filter(Prospect.id == prospect_id).first()
            if prospect:
                prospect.status = status
                prospect.last_updated = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating prospect status: {e}")
            return False
    
    def mark_prospect_visited(self, prospect_id: int, visited: bool = True) -> bool:
        """Mark prospect as visited/unvisited"""
        session = self._get_session()
        
        try:
            prospect = session.query(Prospect).filter(Prospect.id == prospect_id).first()
            if prospect:
                prospect.is_visited = visited
                if visited and not prospect.first_visited_date:
                    prospect.first_visited_date = datetime.now()
                elif not visited:
                    prospect.first_visited_date = None
                prospect.last_updated = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating prospect visited status: {e}")
            return False
    
    def update_prospect_notes(self, prospect_id: int, notes: str) -> bool:
        """Update prospect sales notes"""
        session = self._get_session()
        
        try:
            prospect = session.query(Prospect).filter(Prospect.id == prospect_id).first()
            if prospect:
                prospect.sales_notes = notes
                prospect.last_updated = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating prospect notes: {e}")
            return False
    
    def update_prospect_contact_info(self, prospect_id: int, update_data: Dict) -> bool:
        """Update prospect contact information and details"""
        session = self._get_session()
        
        try:
            prospect = session.query(Prospect).filter(Prospect.id == prospect_id).first()
            if prospect:
                # Update all provided fields
                for key, value in update_data.items():
                    if hasattr(prospect, key):
                        setattr(prospect, key, value)
                
                prospect.last_updated = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating prospect contact info: {e}")
            return False
    
    # COMMUNICATION OPERATIONS
    
    def log_communication(self, prospect_id: int, comm_data: Dict) -> Communication:
        """Log a communication with a prospect"""
        session = self._get_session()
        
        try:
            communication = Communication(
                prospect_id=prospect_id,
                **comm_data
            )
            session.add(communication)
            session.commit()
            session.refresh(communication)
            
            # Update prospect status if it was a successful contact
            if comm_data.get('status') in ['sent', 'delivered', 'answered']:
                self.update_prospect_status(prospect_id, 'contacted')
            
            return communication
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging communication: {e}")
            raise
    
    def get_prospect_communications(self, prospect_id: int) -> List[Communication]:
        """Get all communications for a prospect"""
        session = self._get_session()
        return session.query(Communication).filter(
            Communication.prospect_id == prospect_id
        ).order_by(desc(Communication.created_at)).all()
    
    def get_recent_communications(self, days: int = 7) -> List[Communication]:
        """Get recent communications across all prospects"""
        session = self._get_session()
        since_date = datetime.now() - timedelta(days=days)
        
        return session.query(Communication).filter(
            Communication.created_at >= since_date
        ).order_by(desc(Communication.created_at)).all()
    
    # SEARCH OPERATIONS
    
    def save_search(self, search_data: Dict) -> Search:
        """Save a search record"""
        session = self._get_session()
        
        try:
            search = Search(**search_data)
            session.add(search)
            session.commit()
            session.refresh(search)
            return search
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving search: {e}")
            raise
    
    def link_search_prospect(self, search_id: int, prospect_id: int, 
                           distance: float, ai_score: int, is_new: bool = True) -> SearchResult:
        """Link a search to a prospect"""
        session = self._get_session()
        
        try:
            search_result = SearchResult(
                search_id=search_id,
                prospect_id=prospect_id,
                distance_from_search=distance,
                ai_score_at_time=ai_score,
                was_new_prospect=is_new
            )
            session.add(search_result)
            session.commit()
            session.refresh(search_result)
            return search_result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error linking search prospect: {e}")
            raise
    
    def get_search_history(self, limit: int = 50) -> List[Search]:
        """Get search history"""
        session = self._get_session()
        return session.query(Search).order_by(desc(Search.created_at)).limit(limit).all()
    
    def get_search_by_id(self, search_id: int) -> Optional[Search]:
        """Get search by ID with results"""
        session = self._get_session()
        return session.query(Search).filter(Search.id == search_id).first()
    
    # ANALYTICS OPERATIONS
    
    def get_prospect_stats(self) -> Dict:
        """Get prospect statistics"""
        session = self._get_session()
        
        stats = {
            'total_prospects': session.query(Prospect).count(),
            'contacted': session.query(Prospect).filter(Prospect.status == 'contacted').count(),
            'visited': session.query(Prospect).filter(Prospect.is_visited).count(),
            'high_priority': session.query(Prospect).filter(Prospect.priority == 'high').count(),
            'avg_ai_score': session.query(func.avg(Prospect.ai_score)).scalar() or 0,
        }
        
        # Status breakdown
        status_counts = session.query(
            Prospect.status, func.count(Prospect.id)
        ).group_by(Prospect.status).all()
        
        stats['status_breakdown'] = {status: count for status, count in status_counts}
        
        return stats
    
    def get_communication_stats(self, days: int = 30) -> Dict:
        """Get communication statistics"""
        session = self._get_session()
        since_date = datetime.now() - timedelta(days=days)
        
        stats = {
            'total_communications': session.query(Communication).filter(
                Communication.created_at >= since_date
            ).count(),
        }
        
        # Channel breakdown
        channel_counts = session.query(
            Communication.channel, func.count(Communication.id)
        ).filter(Communication.created_at >= since_date).group_by(Communication.channel).all()
        
        stats['channel_breakdown'] = {channel: count for channel, count in channel_counts}
        
        # Success rates
        success_counts = session.query(
            Communication.status, func.count(Communication.id)
        ).filter(Communication.created_at >= since_date).group_by(Communication.status).all()
        
        stats['success_breakdown'] = {status: count for status, count in success_counts}
        
        return stats
    
    def get_territory_stats(self) -> List[Dict]:
        """Get territory statistics by ZIP code"""
        session = self._get_session()
        
        territory_stats = session.query(
            Prospect.source_zip,
            func.count(Prospect.id).label('prospect_count'),
            func.avg(Prospect.ai_score).label('avg_score'),
            func.avg(Prospect.rating).label('avg_rating'),
            func.count(func.nullif(Prospect.is_visited, False)).label('visited_count')
        ).group_by(Prospect.source_zip).all()
        
        return [
            {
                'zip_code': stat.source_zip,
                'prospect_count': stat.prospect_count,
                'avg_ai_score': round(stat.avg_score or 0, 1),
                'avg_rating': round(stat.avg_rating or 0, 1),
                'visited_count': stat.visited_count or 0
            }
            for stat in territory_stats if stat.source_zip
        ]
    
    # BULK OPERATIONS
    
    def bulk_save_prospects(self, prospects_data: List) -> List[Prospect]:
        """Bulk save prospects"""
        session = self._get_session()
        prospects = []
        
        try:
            for prospect_data in prospects_data:
                # Check if exists
                place_id = _get_prospect_value(prospect_data, 'place_id')
                existing = session.query(Prospect).filter(
                    Prospect.place_id == place_id
                ).first()
                
                if existing:
                    # Update existing
                    if isinstance(prospect_data, dict):
                        for key, value in prospect_data.items():
                            if hasattr(existing, key) and value is not None:
                                setattr(existing, key, value)
                    existing.last_updated = datetime.now()
                    prospects.append(existing)
                else:
                    # Create new
                    if isinstance(prospect_data, dict):
                        prospect = Prospect(**prospect_data)
                    else:
                        prospect = prospect_data
                    session.add(prospect)
                    prospects.append(prospect)
            
            session.commit()
            
            # Refresh all prospects
            for prospect in prospects:
                session.refresh(prospect)
            
            return prospects
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error bulk saving prospects: {e}")
            raise
    
    def search_prospects(self, query: str, fields: List[str] = None) -> List[Prospect]:
        """Search prospects by name, address, or other fields"""
        session = self._get_session()
        
        if fields is None:
            fields = ['name', 'address', 'contact_person']
        
        conditions = []
        for field in fields:
            if hasattr(Prospect, field):
                conditions.append(getattr(Prospect, field).ilike(f'%{query}%'))
        
        if conditions:
            return session.query(Prospect).filter(or_(*conditions)).all()
        
        return []
    
    # DELETE OPERATIONS
    
    def delete_prospect(self, prospect_id: int) -> bool:
        """Delete a prospect and all related data"""
        session = self._get_session()
        
        try:
            # Delete related communications first
            session.query(Communication).filter(
                Communication.prospect_id == prospect_id
            ).delete()
            
            # Delete related search results
            session.query(SearchResult).filter(
                SearchResult.prospect_id == prospect_id
            ).delete()
            
            # Delete the prospect
            result = session.query(Prospect).filter(
                Prospect.id == prospect_id
            ).delete()
            
            session.commit()
            return result > 0
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting prospect {prospect_id}: {e}")
            return False
    
    def delete_search(self, search_id: int) -> bool:
        """Delete a search and its related results"""
        session = self._get_session()
        
        try:
            # Delete related search results first
            session.query(SearchResult).filter(
                SearchResult.search_id == search_id
            ).delete()
            
            # Delete the search
            result = session.query(Search).filter(
                Search.id == search_id
            ).delete()
            
            session.commit()
            return result > 0
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting search {search_id}: {e}")
            return False
    
    def bulk_delete_prospects(self, prospect_ids: List[int]) -> int:
        """Bulk delete prospects and related data"""
        deleted_count = 0
        
        try:
            for prospect_id in prospect_ids:
                if self.delete_prospect(prospect_id):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            return deleted_count

# Global CRM service instance
crm_service = CRMService() 