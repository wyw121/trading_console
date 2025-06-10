# Trading Console Project - GitHub Copilot Instructions

## Project Overview
This is a full-stack cryptocurrency trading console application with:
- **Backend**: Python FastAPI with SQLAlchemy ORM and PostgreSQL database
- **Frontend**: Vue.js 3 with Element Plus UI components and Pinia state management  
- **Trading**: CCXT library for multi-exchange integration and automated strategies
- **Deployment**: Docker containerization with docker-compose

## Technology Stack & Conventions

### Backend (Python/FastAPI)
- Use FastAPI with async/await patterns for all endpoints
- Follow SQLAlchemy 2.0+ syntax with declarative mapping
- Use Pydantic models for request/response validation (schemas.py)
- Implement JWT-based authentication with passlib for password hashing
- Use CCXT library for exchange integrations, handle API keys securely
- Follow the existing router structure in `routers/` directory
- Use dependency injection for database sessions and user authentication
- Implement proper error handling with HTTPException and status codes
- Use APScheduler for background task scheduling

### Frontend (Vue.js 3)
- Use Vue 3 Composition API with `<script setup>` syntax
- Use Element Plus components following their design system
- Implement Pinia stores for state management (auth, exchanges, strategies)
- Use axios for API calls with proper error handling
- Follow the existing component structure with Layout.vue wrapper
- Use Vue Router for navigation with authentication guards
- Implement responsive design patterns
- Use TypeScript-style prop definitions even in JavaScript

### Database Design
- Use SQLAlchemy declarative models with proper relationships
- Implement foreign key constraints and cascade deletions
- Use UTC timestamps for all datetime fields
- Follow the existing schema: Users, ExchangeAccounts, Strategies, Trades, MarketData
- Encrypt sensitive data like API keys before database storage

### Trading Engine
- Use CCXT for unified exchange API access
- Implement strategy pattern for different trading algorithms
- Use numpy for technical indicator calculations (avoid external TA-Lib dependency)
- Handle exchange rate limits and connection errors gracefully
- Implement proper position sizing and risk management
- Log all trading activities for audit trails

### Code Style & Best Practices
- Use descriptive variable names: `exchange_account`, `strategy_config`, `trade_result`
- Follow Python PEP 8 naming conventions: snake_case for variables/functions
- Use Vue.js naming conventions: PascalCase for components, camelCase for props
- Implement proper error boundaries and user feedback
- Add comprehensive logging for debugging and monitoring
- Use environment variables for configuration
- Implement input validation and sanitization
- Follow RESTful API design principles

### Security Considerations
- Never expose API keys in logs or responses
- Implement rate limiting for API endpoints
- Use HTTPS in production environments
- Validate all user inputs and sanitize data
- Implement proper CORS configuration
- Use secure session management
- Encrypt sensitive data at rest

### Development Workflow
- Use Docker for consistent development environment
- Implement database migrations with Alembic
- Use pytest for backend testing
- Use Vue Test Utils for frontend testing
- Follow git conventional commits
- Document API endpoints with FastAPI automatic docs
- Use proper dependency management (requirements.txt, package.json)

### Trading Strategy Development
- Implement modular strategy classes inheriting from base strategy
- Use configuration-based parameter tuning
- Implement backtesting capabilities
- Use proper risk management calculations
- Handle market data efficiently with caching
- Implement strategy performance monitoring

## File Structure Patterns
- Backend routes in `routers/` with clear separation of concerns
- Database models in `database.py` with proper relationships
- Pydantic schemas in `schemas.py` for API validation
- Frontend views in `src/views/` with corresponding router entries
- Shared utilities in `src/utils/` for common functions
- Stores in `src/stores/` for state management

## Common Tasks Guidelines
When implementing new features:
1. Start with database model design and migrations
2. Create Pydantic schemas for request/response validation
3. Implement backend API endpoints with proper error handling
4. Create frontend components with Element Plus UI
5. Add state management if needed
6. Implement proper testing and error scenarios
7. Update documentation and API specs

When working with trading functionality:
1. Always validate exchange connectivity before operations
2. Implement proper error handling for network issues
3. Use testnet/sandbox modes for development
4. Implement position sizing and risk management
5. Log all trading activities with timestamps
6. Handle exchange-specific requirements and limitations

## Performance Optimization
- Use database indexing for frequently queried fields
- Implement connection pooling for database and exchange APIs
- Use caching for market data and configuration
- Optimize frontend bundle size with proper imports
- Use lazy loading for Vue.js routes and components
- Implement proper pagination for large datasets
