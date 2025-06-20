---
description: "Database model and SQLAlchemy development guidelines"
applyTo: "**/database.py"
---

# Database Development Instructions

## SQLAlchemy Model Design
- Use SQLAlchemy 2.0+ syntax with declarative mapping
- Implement proper relationships with foreign key constraints
- Use cascade deletions for related records where appropriate
- Add proper indexes for frequently queried fields
- Use UTC timestamps for all datetime fields
- Implement soft deletes for audit trails when needed

## Database Schema Best Practices
- Follow existing schema patterns: Users, ExchangeAccounts, Strategies, Trades, MarketData
- Use descriptive column names with snake_case convention
- Implement proper data types for different use cases
- Add check constraints for data validation
- Use enums for status fields and predefined values
- Implement proper default values for columns

## Migration Management
- Use Alembic for database migrations
- Write reversible migrations when possible
- Test migrations on development data
- Add proper migration descriptions
- Handle data migrations separately from schema changes
- Backup database before running migrations in production

## Security Considerations
- Encrypt sensitive data like API keys before storage
- Never store plaintext passwords
- Use proper hashing for password fields
- Implement row-level security when needed
- Validate all input data before database operations
- Use parameterized queries to prevent SQL injection

## Performance Optimization
- Add indexes for foreign keys and frequently queried columns
- Use connection pooling for database connections
- Implement proper pagination for large datasets
- Use bulk operations for large data updates
- Monitor query performance and optimize as needed
- Implement proper caching strategies for frequently accessed data
