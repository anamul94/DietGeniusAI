from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Any
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

T = TypeVar('T')

class PaginationResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    items: List[Any] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")

class BasePaginator(ABC):
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def get_query(self, **filters):
        """Return the base query for pagination"""
        pass
    
    def paginate(self, page: int = 1, limit: int = 10, **filters) -> PaginationResult:
        """Execute pagination with filters"""
        query = self.get_query(**filters)
        
        # Get total count
        total = query.count()
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get paginated items
        items = query.offset(offset).limit(limit).all()
        
        # Calculate total pages
        pages = (total + limit - 1) // limit
        
        return PaginationResult(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )