"""
Pagination Utilities
Handles pagination for API responses and database queries
"""

import math
from typing import Any, Dict, Generic, List, Optional, TypeVar
from dataclasses import dataclass
from pydantic import BaseModel, Field
from fastapi import Query, HTTPException, status

T = TypeVar('T')


@dataclass
class PaginationParams:
    """Pagination parameters"""
    page: int
    size: int
    offset: int
    
    def __post_init__(self):
        """Validate and adjust parameters"""
        if self.page < 1:
            self.page = 1
        if self.size < 1:
            self.size = 10
        if self.size > 100:  # Maximum page size
            self.size = 100
        
        self.offset = (self.page - 1) * self.size


class PaginationInfo(BaseModel):
    """Pagination metadata for API responses"""
    current_page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number")
    previous_page: Optional[int] = Field(None, description="Previous page number")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response"""
    data: List[T] = Field(..., description="List of items")
    pagination: PaginationInfo = Field(..., description="Pagination metadata")
    success: bool = Field(True, description="Request success status")
    message: Optional[str] = Field(None, description="Optional message")


class Paginator:
    """
    Utility class for handling pagination
    """
    
    def __init__(self, default_page_size: int = 20, max_page_size: int = 100):
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size
    
    def get_pagination_params(
        self,
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        size: int = Query(20, ge=1, le=100, description="Number of items per page")
    ) -> PaginationParams:
        """
        Get pagination parameters from query parameters
        
        Args:
            page: Page number (1-based)
            size: Page size
            
        Returns:
            PaginationParams object
        """
        return PaginationParams(page=page, size=size, offset=(page - 1) * size)
    
    def create_paginated_response(
        self,
        data: List[T],
        total: int,
        params: PaginationParams,
        message: Optional[str] = None
    ) -> PaginatedResponse[T]:
        """
        Create a paginated response
        
        Args:
            data: List of items for current page
            total: Total number of items
            params: Pagination parameters
            message: Optional message
            
        Returns:
            PaginatedResponse object
        """
        total_pages = math.ceil(total / params.size) if params.size > 0 else 0
        
        pagination_info = PaginationInfo(
            current_page=params.page,
            page_size=params.size,
            total_items=total,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1,
            next_page=params.page + 1 if params.page < total_pages else None,
            previous_page=params.page - 1 if params.page > 1 else None
        )
        
        return PaginatedResponse(
            data=data,
            pagination=pagination_info,
            message=message
        )
    
    def paginate_query(
        self,
        query,
        params: PaginationParams
    ):
        """
        Apply pagination to a SQLAlchemy query
        
        Args:
            query: SQLAlchemy query object
            params: Pagination parameters
            
        Returns:
            Paginated query
        """
        return query.offset(params.offset).limit(params.size)
    
    def get_page_info(
        self,
        total: int,
        params: PaginationParams
    ) -> Dict[str, Any]:
        """
        Get pagination information as dictionary
        
        Args:
            total: Total number of items
            params: Pagination parameters
            
        Returns:
            Dictionary with pagination info
        """
        total_pages = math.ceil(total / params.size) if params.size > 0 else 0
        
        return {
            "current_page": params.page,
            "page_size": params.size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": params.page < total_pages,
            "has_previous": params.page > 1,
            "next_page": params.page + 1 if params.page < total_pages else None,
            "previous_page": params.page - 1 if params.page > 1 else None
        }
    
    def validate_page_bounds(self, page: int, total_pages: int):
        """
        Validate that requested page is within bounds
        
        Args:
            page: Requested page number
            total_pages: Total available pages
            
        Raises:
            HTTPException: If page is out of bounds
        """
        if page > total_pages and total_pages > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page {page} exceeds total pages ({total_pages})"
            )
    
    def get_cursor_params(
        self,
        cursor: Optional[str] = Query(None, description="Cursor for pagination"),
        size: int = Query(20, ge=1, le=100, description="Number of items per page")
    ) -> Dict[str, Any]:
        """
        Get cursor-based pagination parameters
        
        Args:
            cursor: Cursor string
            size: Page size
            
        Returns:
            Dictionary with cursor pagination params
        """
        return {
            "cursor": cursor,
            "size": min(size, self.max_page_size),
            "limit": min(size, self.max_page_size) + 1  # +1 to check if there are more
        }
    
    def create_cursor_response(
        self,
        data: List[T],
        limit: int,
        cursor_field: str = "id"
    ) -> Dict[str, Any]:
        """
        Create cursor-based pagination response
        
        Args:
            data: List of items
            limit: Query limit
            cursor_field: Field to use as cursor
            
        Returns:
            Dictionary with cursor pagination info
        """
        has_next = len(data) > limit - 1
        if has_next:
            data = data[:-1]  # Remove the extra item
        
        next_cursor = None
        if data and has_next:
            next_cursor = str(getattr(data[-1], cursor_field))
        
        return {
            "data": data,
            "has_next": has_next,
            "next_cursor": next_cursor,
            "count": len(data)
        }


class OffsetPaginator(Paginator):
    """
    Offset-based pagination (traditional page/size)
    """
    
    def paginate_list(
        self,
        items: List[T],
        params: PaginationParams
    ) -> List[T]:
        """
        Paginate a list of items
        
        Args:
            items: List of items to paginate
            params: Pagination parameters
            
        Returns:
            List of items for the requested page
        """
        start = params.offset
        end = start + params.size
        return items[start:end]


class CursorPaginator(Paginator):
    """
    Cursor-based pagination for better performance with large datasets
    """
    
    def __init__(self, cursor_field: str = "id"):
        super().__init__()
        self.cursor_field = cursor_field
    
    def get_cursor_query(
        self,
        query,
        cursor: Optional[str] = None,
        size: int = 20
    ):
        """
        Apply cursor-based pagination to a query
        
        Args:
            query: SQLAlchemy query object
            cursor: Cursor value
            size: Page size
            
        Returns:
            Paginated query
        """
        if cursor:
            query = query.filter(getattr(query.column_descriptions[0]['type'], self.cursor_field) > cursor)
        
        return query.limit(size + 1)  # +1 to check if there are more
    
    def extract_cursor(self, item: Any) -> str:
        """
        Extract cursor value from an item
        
        Args:
            item: Database model object
            
        Returns:
            Cursor value as string
        """
        return str(getattr(item, self.cursor_field))


class SearchPaginator(Paginator):
    """
    Pagination with search functionality
    """
    
    def create_search_response(
        self,
        data: List[T],
        total: int,
        search_term: Optional[str],
        params: PaginationParams,
        search_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create paginated search response
        
        Args:
            data: Search results for current page
            total: Total number of matching items
            search_term: Search term used
            params: Pagination parameters
            search_fields: Fields that were searched
            
        Returns:
            Dictionary with search results and pagination
        """
        response = self.create_paginated_response(data, total, params)
        
        # Add search metadata
        search_info = {
            "search_term": search_term,
            "search_fields": search_fields,
            "total_matches": total
        }
        
        return {
            **response.dict(),
            "search": search_info
        }


class AdvancedPaginator(Paginator):
    """
    Advanced pagination with sorting, filtering, and search
    """
    
    def __init__(self, default_page_size: int = 20, max_page_size: int = 100):
        super().__init__(default_page_size, max_page_size)
        self.valid_sort_orders = ['asc', 'desc']
    
    def get_advanced_params(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Items per page"),
        sort: Optional[str] = Query(None, description="Sort field"),
        order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
        search: Optional[str] = Query(None, description="Search term"),
        filters: Optional[str] = Query(None, description="Filter parameters (JSON)")
    ) -> Dict[str, Any]:
        """
        Get advanced pagination parameters
        
        Args:
            page: Page number
            size: Page size
            sort: Sort field
            order: Sort order
            search: Search term
            filters: Filter parameters as JSON string
            
        Returns:
            Dictionary with all pagination parameters
        """
        import json
        
        pagination_params = PaginationParams(page=page, size=size, offset=(page - 1) * size)
        
        filter_dict = {}
        if filters:
            try:
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filter parameters format"
                )
        
        return {
            "pagination": pagination_params,
            "sort": sort,
            "order": order,
            "search": search,
            "filters": filter_dict
        }
    
    def apply_sorting(self, query, sort_field: Optional[str], order: str = "asc"):
        """
        Apply sorting to a query
        
        Args:
            query: SQLAlchemy query object
            sort_field: Field to sort by
            order: Sort order
            
        Returns:
            Sorted query
        """
        if sort_field and hasattr(query.column_descriptions[0]['type'], sort_field):
            sort_column = getattr(query.column_descriptions[0]['type'], sort_field)
            if order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        return query
    
    def apply_filters(self, query, filters: Dict[str, Any], model_class):
        """
        Apply filters to a query
        
        Args:
            query: SQLAlchemy query object
            filters: Dictionary of filters
            model_class: Model class for field reference
            
        Returns:
            Filtered query
        """
        for field, value in filters.items():
            if hasattr(model_class, field) and value is not None:
                field_column = getattr(model_class, field)
                
                if isinstance(value, list):
                    # Filter for multiple values (IN clause)
                    query = query.filter(field_column.in_(value))
                elif isinstance(value, dict):
                    # Range filters
                    if 'min' in value:
                        query = query.filter(field_column >= value['min'])
                    if 'max' in value:
                        query = query.filter(field_column <= value['max'])
                else:
                    # Exact match
                    query = query.filter(field_column == value)
        
        return query


# Utility functions
def create_pagination_links(
    base_url: str,
    total_pages: int,
    current_page: int,
    page_size: int
) -> Dict[str, Optional[str]]:
    """
    Create pagination links for API responses
    
    Args:
        base_url: Base URL for the API endpoint
        total_pages: Total number of pages
        current_page: Current page number
        page_size: Page size
        
    Returns:
        Dictionary with pagination links
    """
    links = {
        "first": f"{base_url}?page=1&size={page_size}" if total_pages > 0 else None,
        "last": f"{base_url}?page={total_pages}&size={page_size}" if total_pages > 0 else None,
        "prev": f"{base_url}?page={current_page - 1}&size={page_size}" if current_page > 1 else None,
        "next": f"{base_url}?page={current_page + 1}&size={page_size}" if current_page < total_pages else None,
        "self": f"{base_url}?page={current_page}&size={page_size}"
    }
    
    return links


# Singleton instances
paginator = Paginator()
offset_paginator = OffsetPaginator()
cursor_paginator = CursorPaginator()
search_paginator = SearchPaginator()
advanced_paginator = AdvancedPaginator()
