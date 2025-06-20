---
description: "Implement a new trading strategy with CCXT integration"
mode: "agent"
tools: ["filesystem"]
---

# Create Trading Strategy

Implement a new trading strategy with CCXT integration and proper risk management.

## Strategy Specifications
- **Strategy Name**: ${input:name:Strategy name (e.g., MovingAverageCrossover)}
- **Description**: ${input:description:Brief description of the trading strategy}
- **Timeframe**: ${input:timeframe:Trading timeframe (1m, 5m, 15m, 1h, 4h, 1d)}
- **Exchange**: ${input:exchange:Target exchange (e.g., binance, okx, bybit)}

## Implementation Requirements

### 1. Strategy Class Structure
- Inherit from the base strategy class
- Implement required abstract methods: `analyze()`, `execute()`, `cleanup()`
- Use proper class documentation and type hints
- Include strategy configuration parameters

### 2. Technical Analysis
- Use numpy for technical indicator calculations
- Implement proper data validation and cleaning
- Handle missing or invalid market data gracefully
- Cache calculations for performance optimization

### 3. Signal Generation
- Implement clear buy/sell signal logic
- Use proper signal strength indicators
- Handle conflicting signals appropriately
- Log all signal generation with reasoning

### 4. Risk Management
- Implement position sizing based on account balance
- Use proper stop-loss and take-profit calculations
- Implement maximum drawdown limits
- Calculate risk-reward ratios for each trade

### 5. Order Execution
- Validate available balance before placing orders
- Handle partial fills and order status updates
- Implement proper order cancellation logic
- Use exchange-specific order types when available

### 6. Performance Monitoring
- Track strategy performance metrics
- Implement profit/loss calculations
- Monitor win rate and average trade duration
- Log all trading activities with timestamps

## File Structure
Please create or update the following files:
- `backend/strategies/${input:name}.py` - Main strategy implementation
- `backend/database.py` - Add strategy configuration model if needed
- `backend/routers/strategies.py` - Add strategy management endpoints
- `backend/schemas.py` - Add strategy configuration schemas

## Required Methods to Implement

### analyze(market_data)
- Analyze market data and generate signals
- Return signal strength and direction
- Include reasoning for the signal

### execute(signal, account_info)
- Execute trades based on generated signals
- Handle order placement and tracking
- Return execution results

### cleanup()
- Clean up resources and connections
- Cancel pending orders if needed
- Save strategy state for recovery

## Configuration Parameters
- Entry/exit thresholds
- Position sizing parameters
- Risk management settings
- Technical indicator periods
- Exchange-specific settings

## Testing Requirements
- Implement backtesting functionality
- Use historical data for strategy validation
- Test with different market conditions
- Validate risk management rules
- Test error handling and recovery

## Documentation
- Add comprehensive docstrings
- Document strategy logic and parameters
- Include usage examples
- Document known limitations and risks

Please implement the strategy following the project's existing patterns and trading best practices.
