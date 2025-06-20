---
description: "Create a new FastAPI endpoint with proper validation and error handling"
mode: "agent"
tools: ["filesystem"]
---

# Create FastAPI Endpoint

Create a new FastAPI endpoint with the following requirements:

## Endpoint Specifications
- **Path**: ${input:path:Enter the API endpoint path (e.g., /users/{user_id})}
- **Method**: ${input:method:HTTP method (GET, POST, PUT, DELETE)}
- **Description**: ${input:description:Brief description of the endpoint functionality}

## Implementation Requirements

### 1. Router Setup
- Add the endpoint to the appropriate router in `backend/routers/`
- Use proper router prefix and tags
- Include the endpoint in the router's dependency injection

### 2. Request/Response Models
- Create Pydantic models for request validation in `schemas.py`
- Create response models with proper field validation
- Include example values in the schema definitions

### 3. Database Operations
- Use async SQLAlchemy session with dependency injection
- Implement proper error handling for database operations
- Use appropriate database queries with joins if needed
- Handle potential duplicate entries and constraint violations

### 4. Authentication & Authorization
- Add authentication dependency if required
- Implement proper authorization checks
- Handle authentication errors gracefully

### 5. Error Handling
- Use HTTPException for different error scenarios
- Return appropriate HTTP status codes
- Provide meaningful error messages
- Log errors with appropriate severity levels

### 6. Documentation
- Add comprehensive docstrings
- Include parameter descriptions
- Add response examples
- Document possible error scenarios

## File Structure
Please create or update the following files:
- `backend/routers/{router_name}.py` - Main endpoint implementation
- `backend/schemas.py` - Request/response models
- `backend/database.py` - Database model updates if needed

## Testing Considerations
- Ensure the endpoint handles edge cases
- Validate input parameters thoroughly
- Test with invalid authentication tokens
- Verify proper database transaction handling

Please implement the endpoint following the project's existing patterns and coding standards.
