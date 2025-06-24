"""
Trading Console Error Handler
优化的错误处理和日志记录
"""
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime

class TradingConsoleLogger:
    """Custom logger for trading console"""
    
    def __init__(self, name: str = "trading_console"):
        self.logger = logging.getLogger(name)
        
        # Only add handlers if they don't exist
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with proper formatting"""
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, error: Optional[Exception] = None, extra: Optional[Dict] = None):
        """Log error message"""
        if error:
            self.logger.error(f"{message}: {str(error)}", extra=extra)
        else:
            self.logger.error(message, extra=extra)
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra)

class ExchangeErrorHandler:
    """Handle exchange-specific errors"""
    
    def __init__(self):
        self.logger = TradingConsoleLogger("exchange_handler")
        self.error_counts = {}
        self.max_retries = 3
    
    def handle_okx_error(self, error: Exception, account_name: str) -> str:
        """Handle OKX-specific errors"""
        error_str = str(error)
        
        # Count errors for this account
        if account_name not in self.error_counts:
            self.error_counts[account_name] = 0
        self.error_counts[account_name] += 1
        
        # OKX specific error patterns
        if "okex GET https://www.okx.com" in error_str:
            if "timeout" in error_str.lower() or "exceeded" in error_str.lower():
                self.logger.warning(f"OKX API timeout for {account_name} (attempt {self.error_counts[account_name]})")
                return "网络超时，正在使用模拟数据"
            else:
                self.logger.warning(f"OKX API connection failed for {account_name}")
                return "连接失败，正在使用模拟数据"
        
        # Authentication errors
        if "Invalid API" in error_str or "Authentication" in error_str:
            self.logger.error(f"OKX API authentication failed for {account_name}")
            return "API认证失败，请检查密钥配置"
        
        # Rate limit errors
        if "rate limit" in error_str.lower():
            self.logger.warning(f"OKX API rate limit hit for {account_name}")
            return "请求过于频繁，请稍后再试"
        
        # Generic error
        self.logger.error(f"OKX API error for {account_name}", error)
        return "交易所连接异常，正在使用模拟数据"
    
    def should_use_mock(self, account_name: str) -> bool:
        """Determine if we should use mock mode for this account"""
        return self.error_counts.get(account_name, 0) >= self.max_retries
    
    def reset_error_count(self, account_name: str):
        """Reset error count for successful connection"""
        if account_name in self.error_counts:
            self.error_counts[account_name] = 0

# Global instances
console_logger = TradingConsoleLogger()
error_handler = ExchangeErrorHandler()
