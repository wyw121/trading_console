# New Trading Strategy Implementation

Your goal is to implement a new trading strategy for the cryptocurrency trading console.

## Requirements

Ask for the strategy details if not provided:
- Strategy name and description
- Entry and exit conditions
- Technical indicators needed
- Risk management parameters
- Target timeframes and symbols

## Implementation Guidelines

### Backend Strategy Class
- Create a new strategy class in `trading_engine.py` inheriting from base strategy
- Implement `check_strategy_signal()` method with proper signal logic
- Use numpy for technical indicator calculations (no TA-Lib dependency)
- Add configuration parameters to database schema if needed
- Implement proper error handling and logging

### Database Schema Updates
- Update `Strategy` model in `database.py` if new parameters needed
- Create Alembic migration for schema changes
- Update Pydantic schemas in `schemas.py` for API validation

### API Integration
- Update strategy router endpoints if new configuration options needed
- Ensure proper validation and error responses
- Test with different parameter combinations

### Frontend Integration
- Update strategy creation/editing forms in `Strategies.vue`
- Add new parameter inputs with proper validation
- Update strategy display components
- Test user interface thoroughly

## Code Structure
```python
class NewStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        # Initialize strategy-specific parameters
    
    async def check_strategy_signal(self, market_data):
        # Implement signal logic
        # Return 'buy', 'sell', or None
        pass
    
    def calculate_indicators(self, prices):
        # Implement technical indicators using numpy
        pass
```

## Testing Checklist
- [ ] Strategy logic validation with historical data
- [ ] Parameter validation and edge cases
- [ ] API endpoint testing
- [ ] Frontend form validation
- [ ] Database migration testing
- [ ] Error handling scenarios

## Risk Management
- Implement position sizing calculations
- Add stop-loss and take-profit logic
- Validate risk parameters
- Include maximum drawdown limits
- Test with different market conditions
