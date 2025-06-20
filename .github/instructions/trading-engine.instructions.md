---
description: "Trading engine and CCXT integration guidelines"
applyTo: "**/*trading*/**/*.py"
---

# Trading Engine Development Instructions

## CCXT Integration
- Always use try-catch blocks for exchange API calls
- Implement proper rate limiting to respect exchange limits
- Handle network timeouts and connection errors gracefully
- Use exchange-specific error handling for different error types
- Implement retry logic with exponential backoff for transient failures
- Log all API calls with request/response details (excluding sensitive data)

## Trading Strategy Implementation
- Inherit from base strategy class for consistency
- Implement modular strategy patterns
- Use configuration-based parameter tuning
- Implement proper backtesting capabilities
- Use numpy for technical indicator calculations (avoid TA-Lib dependency)
- Handle market data efficiently with caching mechanisms

## Risk Management
- Always validate available balance before placing orders
- Implement proper position sizing calculations
- Use stop-loss and take-profit orders when supported
- Implement maximum drawdown limits
- Calculate and monitor risk-reward ratios
- Implement portfolio-level risk controls

## Order Management
- Validate order parameters before submission
- Handle partial fills and order status updates
- Implement proper order cancellation logic
- Track order execution and slippage
- Handle exchange-specific order types and requirements
- Log all order activities with timestamps

## Market Data Handling
- Implement efficient data fetching and caching
- Handle websocket connections for real-time data
- Implement proper data validation and cleaning
- Use appropriate timeframes for different strategies
- Handle market closures and trading hours
- Implement data backup and recovery mechanisms

## Security and API Key Management
- Never expose API keys in logs or responses
- Use environment variables for API key storage
- Implement proper encryption for stored API keys
- Use read-only API keys when possible
- Implement IP whitelisting when supported by exchange
- Regularly rotate API keys and monitor usage
