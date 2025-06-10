# API Endpoint Development

Your goal is to create a new API endpoint for the trading console backend.

## Requirements

Ask for endpoint details if not provided:
- Endpoint purpose and functionality
- HTTP method (GET, POST, PUT, DELETE)
- Request/response data structure
- Authentication requirements
- Validation rules

## Implementation Guidelines

### FastAPI Endpoint Structure
- Create endpoint in appropriate router file (`routers/`)
- Use proper HTTP status codes and error handling
- Implement request/response validation with Pydantic schemas
- Add authentication dependency if required
- Include comprehensive docstrings

### Database Operations
- Use SQLAlchemy async sessions with dependency injection
- Implement proper error handling for database operations
- Use transactions for multi-step operations
- Add proper indexing for query optimization

### Schema Validation
- Create Pydantic models in `schemas.py` for request/response validation
- Use proper field validation and error messages
- Implement optional fields with default values
- Add examples for API documentation

### Security & Validation
- Validate user permissions and ownership
- Sanitize input data
- Implement rate limiting if needed
- Use proper CORS headers
- Validate file uploads if applicable

## Code Template
```python
# In routers/example.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db, User
from auth import get_current_user
from schemas import RequestSchema, ResponseSchema

router = APIRouter(prefix="/api/example", tags=["example"])

@router.post("/", response_model=ResponseSchema)
async def create_item(
    request: RequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new item with proper validation and error handling.
    """
    try:
        # Validate user permissions
        # Process request data
        # Database operations
        # Return response
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

## Testing Requirements
- [ ] Valid request/response testing
- [ ] Authentication and authorization testing
- [ ] Input validation and error cases
- [ ] Database constraint testing
- [ ] Performance testing with large datasets
- [ ] API documentation verification

## Error Handling
- Use appropriate HTTP status codes
- Provide clear error messages
- Log errors for debugging
- Handle database connection issues
- Validate foreign key constraints

## Documentation
- Add comprehensive docstrings
- Include request/response examples
- Document error codes and messages
- Update API documentation
- Add usage examples
