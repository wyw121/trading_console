"""
OKX API 合规性管理器
处理权限验证、IP白名单检查、速率限制等OKX API要求
"""

import json
import requests
import asyncio
import ccxt
import ipaddress
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from database import ExchangeAccount
import logging

logger = logging.getLogger(__name__)

@dataclass
class OKXPermission:
    """OKX API权限枚举"""
    READ = "read"
    TRADE = "trade" 
    WITHDRAW = "withdraw"

@dataclass
class ValidationResult:
    """API验证结果"""
    is_valid: bool
    permissions: List[str]
    ip_address: Optional[str]
    error_message: Optional[str]
    rate_limit_info: Optional[Dict]

class OKXComplianceManager:
    """OKX API合规性管理器"""
    
    def __init__(self, use_proxy: bool = True):
        self.use_proxy = use_proxy
        self.proxy_config = self._get_proxy_config() if use_proxy else None
        
    def _get_proxy_config(self) -> Dict:
        """获取代理配置"""
        return {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
    
    async def validate_api_credentials(self, 
                                     api_key: str, 
                                     api_secret: str, 
                                     passphrase: str,
                                     is_testnet: bool = False) -> ValidationResult:
        """
        验证OKX API凭据并获取权限信息
        """
        try:
            # 创建CCXT OKX实例
            exchange_config = {
                'apiKey': api_key,
                'secret': api_secret,
                'password': passphrase,
                'sandbox': is_testnet,
                'enableRateLimit': True,
                'timeout': 30000,
            }
            
            # 如果使用代理，添加代理配置
            if self.proxy_config:
                exchange_config['proxies'] = self.proxy_config
            
            exchange = ccxt.okx(exchange_config)
            
            # 测试API连接和权限
            balance_info = await self._test_balance_permission(exchange)
            trade_permission = await self._test_trade_permission(exchange)
            
            # 获取当前IP地址
            current_ip = await self._get_current_ip()
            
            # 确定权限
            permissions = [OKXPermission.READ]
            if trade_permission:
                permissions.append(OKXPermission.TRADE)
                
            # 检查提币权限（通过尝试获取提币地址）
            withdraw_permission = await self._test_withdraw_permission(exchange)
            if withdraw_permission:
                permissions.append(OKXPermission.WITHDRAW)
            
            # 获取速率限制信息
            rate_limit_info = self._extract_rate_limit_info(exchange)
            
            return ValidationResult(
                is_valid=True,
                permissions=permissions,
                ip_address=current_ip,
                error_message=None,
                rate_limit_info=rate_limit_info
            )
            
        except ccxt.AuthenticationError as e:
            logger.error(f"OKX API认证失败: {e}")
            return ValidationResult(
                is_valid=False,
                permissions=[],
                ip_address=None,
                error_message=f"API认证失败: {str(e)}",
                rate_limit_info=None
            )
        except ccxt.PermissionDenied as e:
            logger.error(f"OKX API权限被拒绝: {e}")
            return ValidationResult(
                is_valid=False,
                permissions=[],
                ip_address=None,
                error_message=f"权限被拒绝: {str(e)}",
                rate_limit_info=None
            )
        except Exception as e:
            logger.error(f"OKX API验证异常: {e}")
            return ValidationResult(
                is_valid=False,
                permissions=[],
                ip_address=None,
                error_message=f"验证失败: {str(e)}",
                rate_limit_info=None
            )
    
    async def _test_balance_permission(self, exchange) -> bool:
        """测试读取权限（获取余额）"""
        try:
            await exchange.fetch_balance()
            return True
        except:
            return False
    
    async def _test_trade_permission(self, exchange) -> bool:
        """测试交易权限（获取订单历史）"""
        try:
            # 尝试获取订单历史，这需要交易权限
            await exchange.fetch_orders('BTC/USDT', limit=1)
            return True
        except ccxt.PermissionDenied:
            return False
        except:
            # 其他错误可能是网络问题，不一定是权限问题
            return True
    
    async def _test_withdraw_permission(self, exchange) -> bool:
        """测试提币权限"""
        try:
            # 尝试获取提币地址，这需要提币权限
            await exchange.fetch_deposit_address('BTC')
            return True
        except ccxt.PermissionDenied:
            return False
        except:
            # 其他错误可能是网络问题，不一定是权限问题
            return False
    
    async def _get_current_ip(self) -> Optional[str]:
        """获取当前外网IP地址"""
        try:
            if self.proxy_config:
                # 通过代理获取IP
                response = requests.get('https://httpbin.org/ip', 
                                      proxies=self.proxy_config, 
                                      timeout=10)
                return response.json().get('origin', '').split(',')[0].strip()
            else:
                # 直接获取IP
                response = requests.get('https://httpbin.org/ip', timeout=10)
                return response.json().get('origin', '').split(',')[0].strip()
        except Exception as e:
            logger.error(f"获取IP地址失败: {e}")
            return None
    
    def _extract_rate_limit_info(self, exchange) -> Dict:
        """提取速率限制信息"""
        try:
            # OKX的速率限制信息通常在响应头中
            rate_limits = exchange.rateLimit
            return {
                'rate_limit': rate_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
        except:
            return {}
    
    def validate_ip_whitelist(self, ip_address: str, whitelist: str) -> bool:
        """验证IP是否在白名单中"""
        if not whitelist or not ip_address:
            return True
        
        try:
            # 解析白名单（支持IP地址和CIDR格式）
            allowed_ips = [ip.strip() for ip in whitelist.split(',')]
            user_ip = ipaddress.ip_address(ip_address)
            
            for allowed_ip in allowed_ips:
                try:
                    # 检查是否是CIDR格式
                    if '/' in allowed_ip:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if user_ip in network:
                            return True
                    else:
                        # 单个IP地址
                        if user_ip == ipaddress.ip_address(allowed_ip):
                            return True
                except ValueError:
                    continue
            
            return False
        except Exception as e:
            logger.error(f"IP白名单验证失败: {e}")
            return False
    
    def check_rate_limit(self, account: ExchangeAccount) -> Tuple[bool, Optional[datetime]]:
        """检查是否超过速率限制"""
        if not account.rate_limit_reset or not account.rate_limit_remaining:
            return True, None
        
        now = datetime.utcnow()
        
        # 如果重置时间已过，允许请求
        if now >= account.rate_limit_reset:
            return True, None
        
        # 如果还有剩余次数，允许请求
        if account.rate_limit_remaining > 0:
            return True, account.rate_limit_reset
        
        # 超过限制
        return False, account.rate_limit_reset
    
    def update_rate_limit_info(self, 
                              db: Session, 
                              account: ExchangeAccount, 
                              remaining: int, 
                              reset_time: datetime):
        """更新速率限制信息"""
        account.rate_limit_remaining = remaining
        account.rate_limit_reset = reset_time
        db.commit()
    
    def update_validation_status(self, 
                                db: Session, 
                                account: ExchangeAccount, 
                                result: ValidationResult):
        """更新账户验证状态"""
        account.last_validation = datetime.utcnow()
        account.validation_status = "valid" if result.is_valid else "invalid"
        account.validation_error = result.error_message
        
        if result.permissions:
            account.permissions = json.dumps(result.permissions)
        
        if result.rate_limit_info:
            account.rate_limit_remaining = result.rate_limit_info.get('remaining')
            if result.rate_limit_info.get('reset_time'):
                account.rate_limit_reset = datetime.fromisoformat(
                    result.rate_limit_info['reset_time']
                )
        
        db.commit()
    
    def get_permission_requirements(self, operation: str) -> List[str]:
        """获取特定操作所需的权限"""
        permission_map = {
            'fetch_balance': [OKXPermission.READ],
            'fetch_orders': [OKXPermission.READ],
            'fetch_order': [OKXPermission.READ],
            'fetch_ticker': [OKXPermission.READ],
            'fetch_ohlcv': [OKXPermission.READ],
            'create_order': [OKXPermission.TRADE],
            'cancel_order': [OKXPermission.TRADE],
            'cancel_all_orders': [OKXPermission.TRADE],
            'withdraw': [OKXPermission.WITHDRAW],
            'fetch_deposit_address': [OKXPermission.WITHDRAW]
        }
        
        return permission_map.get(operation, [OKXPermission.READ])
    
    def has_required_permissions(self, 
                                account: ExchangeAccount, 
                                operation: str) -> bool:
        """检查账户是否有执行特定操作的权限"""
        if not account.permissions:
            return False
        
        try:
            account_permissions = json.loads(account.permissions)
            required_permissions = self.get_permission_requirements(operation)
            
            return all(perm in account_permissions for perm in required_permissions)
        except:
            return False

# 全局实例
okx_compliance = OKXComplianceManager()
