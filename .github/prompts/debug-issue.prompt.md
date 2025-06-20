---
description: "Debug and fix issues in the trading console application"
mode: "agent"
tools: ["filesystem", "terminal"]
---

# Debug Trading Console Issue

Systematically debug and fix issues in the trading console application.

## Issue Description
- **Problem**: ${input:problem:Describe the issue you're experiencing}
- **Component**: ${input:component:Which part of the system (backend, frontend, trading engine)}
- **Error Message**: ${input:error:Any error messages or logs}

## Debugging Process

### 1. Log Analysis
- Check application logs for error details
- Look for stack traces and error patterns
- Check database connection and query logs
- Review exchange API call logs

### 2. Environment Validation
- Verify all environment variables are set correctly
- Check database connectivity and migrations
- Validate exchange API keys and permissions
- Test network connectivity and proxy settings

### 3. Code Review
- Review recent code changes that might have caused the issue
- Check for common patterns: null pointer exceptions, async/await issues
- Validate API endpoint implementations
- Review database queries and relationships

### 4. System Dependencies
- Check if all required services are running (database, Redis, etc.)
- Verify Python virtual environment is activated
- Check Node.js dependencies are installed
- Validate Docker containers are running if using containerization

## Common Issue Categories

### Backend Issues
- FastAPI server startup problems
- Database connection errors
- Authentication and JWT token issues
- CCXT exchange connectivity problems
- API endpoint errors and validation issues

### Frontend Issues
- Vue.js component rendering problems
- Pinia store state management issues
- API call failures and error handling
- Element Plus component integration problems
- Router navigation and authentication guard issues

### Trading Engine Issues
- Exchange API authentication failures
- Market data fetching problems
- Order execution and tracking issues
- Strategy calculation errors
- Risk management validation problems

### Infrastructure Issues
- Docker container configuration problems
- Database migration failures
- Proxy and network connectivity issues
- SSL certificate and HTTPS configuration
- Environment variable configuration problems

## Debugging Tools and Commands

### Backend Debugging
```bash
# Check server logs
tail -f backend/logs/app.log

# Test database connection
python backend/test_db_connection.py

# Validate API endpoints
curl -X GET http://localhost:8000/api/v1/health

# Check environment variables
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

### Frontend Debugging
```bash
# Check build errors
npm run build

# Test development server
npm run dev

# Check browser console for JavaScript errors
# Validate API calls in Network tab
```

### Trading Engine Debugging
```bash
# Test exchange connectivity
python backend/test_exchange_connection.py

# Validate API keys
python backend/validate_api_keys.py

# Check market data fetching
python backend/test_market_data.py
```

## Resolution Steps

### 1. Immediate Fixes
- Apply quick fixes for obvious issues
- Update configuration files if needed
- Restart services if required
- Clear caches and temporary files

### 2. Code Updates
- Fix identified bugs in the codebase
- Update error handling and logging
- Improve input validation
- Add missing error checks

### 3. Testing and Validation
- Test the fix in development environment
- Validate with different scenarios
- Check for regression issues
- Update unit tests if needed

### 4. Documentation
- Document the issue and resolution
- Update troubleshooting guides
- Add monitoring for similar issues
- Update deployment procedures if needed

## Prevention Measures
- Add better error handling and logging
- Implement health checks and monitoring
- Add unit tests for critical functionality
- Improve input validation and sanitization
- Update documentation and operational procedures

Please analyze the issue systematically and provide a comprehensive solution with prevention measures.
