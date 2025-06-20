---
description: "Review code for security vulnerabilities and best practices"
mode: "agent"
tools: ["filesystem"]
---

# Security Code Review

Perform a comprehensive security review of the trading console codebase.

## Review Scope
- **Files to Review**: ${input:files:Specify files or directories to review (e.g., backend/routers/, frontend/src/)}
- **Focus Area**: ${input:focus:Specific security concern (API keys, authentication, input validation, etc.)}

## Security Review Checklist

### 1. Authentication & Authorization
- [ ] JWT token implementation and validation
- [ ] Password hashing using proper algorithms (bcrypt)
- [ ] Session management and token expiration
- [ ] Role-based access control implementation
- [ ] Authentication bypass vulnerabilities
- [ ] Proper logout and session invalidation

### 2. API Security
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] Cross-site scripting (XSS) protection
- [ ] Cross-site request forgery (CSRF) protection
- [ ] Rate limiting implementation
- [ ] API endpoint authentication requirements

### 3. Data Protection
- [ ] Sensitive data encryption at rest
- [ ] API key storage and encryption
- [ ] Database connection security
- [ ] Personal data handling compliance
- [ ] Secure data transmission (HTTPS)
- [ ] Proper error message handling (no data leakage)

### 4. Configuration Security
- [ ] Environment variable usage for secrets
- [ ] Default password and configuration changes
- [ ] Debug mode disabled in production
- [ ] Proper CORS configuration
- [ ] Security headers implementation
- [ ] File upload security (if applicable)

### 5. Trading-Specific Security
- [ ] API key validation and permissions
- [ ] Order validation and limits
- [ ] Balance verification before trades
- [ ] Transaction logging and audit trails
- [ ] Exchange API rate limiting compliance
- [ ] Withdrawal and transfer restrictions

### 6. Infrastructure Security
- [ ] Docker container security
- [ ] Network security and firewalls
- [ ] SSL/TLS configuration
- [ ] Proxy configuration security
- [ ] Database access restrictions
- [ ] Logging security (no sensitive data in logs)

## Common Vulnerabilities to Check

### Backend (Python/FastAPI)
```python
# Check for these patterns:

# 1. Insecure direct object references
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    # Missing authorization check

# 2. SQL injection vulnerabilities
query = f"SELECT * FROM users WHERE id = {user_id}"

# 3. Weak password requirements
if len(password) < 6:  # Too weak

# 4. API key exposure
logger.info(f"Using API key: {api_key}")  # Logging sensitive data

# 5. Missing input validation
def transfer_funds(amount: float):
    # No validation for negative amounts
```

### Frontend (Vue.js)
```javascript
// Check for these patterns:

// 1. XSS vulnerabilities
innerHTML = userInput  // Unescaped user input

// 2. Sensitive data in client-side storage
localStorage.setItem('apiKey', apiKey)  // Insecure storage

// 3. Weak client-side validation only
if (amount > 0) {  // Server-side validation also required
    submitOrder()
}

// 4. Hardcoded credentials
const API_KEY = 'hardcoded-key'  // Should use environment variables
```

## Review Process

### 1. Static Code Analysis
- Review code for common vulnerability patterns
- Check for hardcoded secrets and credentials
- Validate input sanitization and output encoding
- Check for proper error handling

### 2. Authentication Flow Review
- Trace authentication and authorization flows
- Verify token generation and validation
- Check for privilege escalation vulnerabilities
- Review session management implementation

### 3. API Endpoint Security
- Review each API endpoint for authentication requirements
- Check input validation and rate limiting
- Verify proper error handling and responses
- Check for information disclosure vulnerabilities

### 4. Data Flow Analysis
- Trace sensitive data through the application
- Verify encryption and secure transmission
- Check for data leakage in logs and error messages
- Review data retention and deletion practices

## Security Recommendations

### High Priority Issues
- Fix any authentication bypass vulnerabilities
- Implement proper input validation and sanitization
- Secure API key storage and handling
- Add rate limiting to prevent abuse

### Medium Priority Issues
- Implement comprehensive logging and monitoring
- Add security headers and CORS configuration
- Review and update error handling
- Implement proper session management

### Best Practices
- Regular security updates for dependencies
- Implement security testing in CI/CD pipeline
- Add security monitoring and alerting
- Regular penetration testing and code reviews

## Deliverables
1. List of identified security vulnerabilities
2. Risk assessment for each vulnerability
3. Specific remediation recommendations
4. Code examples for secure implementations
5. Security checklist for future development

Please provide a detailed security assessment with specific findings and actionable recommendations.
