---
description: "Backend API development guidelines for FastAPI endpoints"
applyTo: "backend/**/*.py"
---

# Backend API Development Instructions

## FastAPI Endpoint Development
- Always use async/await for database operations
- Implement proper dependency injection for database sessions
- Use Pydantic models for request/response validation
- Return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Implement proper error handling with HTTPException
- Add comprehensive logging for debugging
- Use router prefixes for API versioning (/api/v1/)

## Database Operations
- Use SQLAlchemy 2.0+ syntax with async session
- Implement proper transaction handling
- Use database indexes for performance optimization
- Handle database connection errors gracefully
- Implement proper cascade deletions for related records

## Security Best Practices
- Validate all input parameters
- Never expose sensitive data in responses
- Implement rate limiting for API endpoints
- Use JWT tokens for authentication
- Encrypt sensitive data before storing in database
- Implement proper CORS configuration

## Error Handling
- Use try-catch blocks for all external API calls
- Log errors with appropriate severity levels
- Return user-friendly error messages
- Implement retry logic for transient failures
- Handle network timeouts gracefully

## Trading API Specific
- Always validate exchange connectivity before operations
- Handle exchange rate limits and connection errors
- Use testnet/sandbox modes for development
- Implement proper position sizing calculations
- Log all trading activities with timestamps
- Handle exchange-specific requirements and limitations
