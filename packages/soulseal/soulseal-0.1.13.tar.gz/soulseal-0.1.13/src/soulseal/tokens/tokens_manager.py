from typing import Dict, Any, Optional, Union, List, Tuple, Self
from datetime import datetime, timedelta, timezone
from fastapi import Response
from pathlib import Path
from calendar import timegm
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from voidring import IndexedRocksDB, CachedRocksDB

import os
import jwt
import logging
import uuid
import time

from ..schemas import Result
from .token_schemas import (
    TokenType, TokenClaims, TokenResult,
    JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
    get_current_timestamp, get_expires_timestamp
)
from .blacklist import TokenBlacklistProvider, MemoryTokenBlacklist, RedisTokenBlacklist

__JWT_SECRET_KEY__ = os.getenv("FASTAPI_SECRET_KEY", "MY-SECRET-KEY")
__JWT_ALGORITHM__ = os.getenv("FASTAPI_ALGORITHM", "HS256")
__ACCESS_TOKEN_EXPIRE_MINUTES__ = int(os.getenv("FASTAPI_ACCESS_TOKEN_EXPIRE_MINUTES", 5))
__REFRESH_TOKEN_EXPIRE_DAYS__ = int(os.getenv("FASTAPI_REFRESH_TOKEN_EXPIRE_DAYS", 30))

class TokenType(str, Enum):
    """令牌类型"""
    ACCESS = "access"
    REFRESH = "refresh"

class TokensManager:
    """令牌管理器，专注于刷新令牌的持久化管理
    
    主要功能:
    1. 持久化存储刷新令牌（使用RocksDB）
    2. 创建、验证、续订和刷新访问令牌
    """
    
    def __init__(self, db: IndexedRocksDB, blacklist_provider: TokenBlacklistProvider = None):
        """初始化令牌管理器
        
        Args:
            db: RocksDB实例，用于持久化存储刷新令牌
            blacklist_provider: 黑名单提供者，默认为MemoryTokenBlacklist
        """
        self._logger = logging.getLogger(__name__)
        self._cache = CachedRocksDB(db)
        self._token_blacklist = blacklist_provider or MemoryTokenBlacklist()
        
    def get_refresh_token(self, user_id: str, device_id: str) -> str:
        """获取刷新令牌
        
        从数据库中获取用户特定设备的刷新令牌。
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            str: JWT格式的刷新令牌，如果不存在则返回None
        """
        token_key = TokenClaims.get_refresh_token_key(user_id, device_id)
        token_claims = self._cache.get(token_key)
        if token_claims:
            return token_claims.jwt_encode()
        return None
    
    def update_refresh_token(self, user_id: str, username: str, roles: List[str], device_id: str) -> TokenClaims:
        """保存刷新令牌到数据库
        
        创建新的刷新令牌并保存到数据库中。
        通常在用户登录时调用。
        
        Args:
            user_id: 用户ID
            username: 用户名
            roles: 用户角色列表
            device_id: 设备ID
            
        Returns:
            TokenClaims: 创建的刷新令牌对象
        """
        # 创建刷新令牌
        claims = TokenClaims.create_refresh_token(user_id, username, roles, device_id)

        # 保存刷新令牌到数据库
        token_key = TokenClaims.get_refresh_token_key(user_id, device_id)
        self._cache.put(token_key, claims)

        self._logger.info(f"已更新刷新令牌: {claims}")
        return claims
    
    def revoke_refresh_token(self, user_id: str, device_id: str) -> None:
        """撤销数据库中的刷新令牌"""
        token_key = TokenClaims.get_refresh_token_key(user_id, device_id)
        claims = self._cache.get(token_key)
        if claims:
            claims.revoke()
            self._cache.put(token_key, claims)
            self._logger.info(f"刷新令牌已撤销: {token_key}")
    
    def refresh_access_token(self, user_id: str, username: str, roles: List[str], device_id: str) -> Result[Dict[str, Any]]:
        """使用刷新令牌创建新的访问令牌"""
        # 先检查黑名单
        token_id = f"{user_id}:{device_id}"
        if hasattr(self, '_token_blacklist') and self._token_blacklist.contains(token_id):
            self._logger.warning(f"访问令牌已经撤销: {token_id}")
            return Result.fail("访问令牌已经撤销")
        
        # 获取刷新令牌
        refresh_token = self.get_refresh_token(user_id, device_id)
        if not refresh_token:
            self._logger.warning(f"刷新令牌不存在: {user_id}:{device_id}")
            return Result.fail("刷新令牌不存在，请重新登录")
        
        try:
            # 验证刷新令牌
            refresh_data = jwt.decode(
                refresh_token,
                key=JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM]
            )
            
            # 检查令牌类型
            if refresh_data.get("token_type") != TokenType.REFRESH:
                self._logger.warning(f"无效的刷新令牌类型: {refresh_data.get('token_type')}")
                return Result.fail("无效的刷新令牌类型，请重新登录")
            
            # 创建新的访问令牌
            claims = TokenClaims.create_access_token(user_id, username, roles, device_id)
            access_token = claims.jwt_encode()
            
            # 刷新成功后自动延长刷新令牌有效期
            extend_result = self.extend_refresh_token(user_id, device_id)
            if extend_result.is_fail():
                self._logger.warning(f"延长刷新令牌有效期失败: {extend_result.error}")
            
            self._logger.info(f"已刷新访问令牌: {user_id}")
            return Result.ok(
                data={
                    "access_token": access_token,
                    **jwt.decode(
                        access_token,
                        key=JWT_SECRET_KEY,
                        algorithms=[JWT_ALGORITHM],
                        options={'verify_exp': False}
                    )
                },
                message="访问令牌刷新成功"
            )
            
        except jwt.ExpiredSignatureError:
            self._logger.warning(f"刷新令牌已过期: {user_id}")
            return Result.fail("刷新令牌已过期，请重新登录")
            
        except Exception as e:
            self._logger.error(f"刷新访问令牌失败: {str(e)}")
            return Result.fail(f"刷新访问令牌失败: {str(e)}")
    
    def renew_access_token(self, user_id: str, username: str, roles: List[str], device_id: str) -> Result[Dict[str, Any]]:
        """续订尚未过期但即将到期的访问令牌
        
        与refresh_access_token不同，renew_access_token用于令牌尚未过期但即将到期的情况，
        不需要验证刷新令牌，直接创建新的访问令牌。
        
        Args:
            user_id: 用户ID
            username: 用户名
            roles: 用户角色列表
            device_id: 设备ID
            
        Returns:
            Result: 续订结果，包含新的访问令牌或错误信息
        """
        # 先检查黑名单
        token_id = f"{user_id}:{device_id}"
        if hasattr(self, '_token_blacklist') and self._token_blacklist.contains(token_id):
            self._logger.warning(f"访问令牌已经撤销: {token_id}")
            return Result.fail("访问令牌已经撤销")

        try:
            # 创建新的访问令牌
            claims = TokenClaims.create_access_token(user_id, username, roles, device_id)
            access_token = claims.jwt_encode()
            
            self._logger.info(f"已续订访问令牌: {user_id}")
            return Result.ok(
                data={
                    "access_token": access_token,
                    **jwt.decode(
                        access_token,
                        key=JWT_SECRET_KEY,
                        algorithms=[JWT_ALGORITHM],
                        options={'verify_exp': False}
                    )
                },
                message="访问令牌续订成功"
            )
            
        except Exception as e:
            self._logger.error(f"续订访问令牌失败: {str(e)}")
            return Result.fail(f"续订访问令牌失败: {str(e)}")
    
    def revoke_access_token(self, user_id: str, device_id: str) -> None:
        """撤销访问令牌
        
        将访问令牌加入黑名单，使其不再有效。
        通常在用户注销或更改密码时调用。
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
        """
        token_id = f"{user_id}:{device_id}"
        expires_at = get_expires_timestamp(days=REFRESH_TOKEN_EXPIRE_DAYS)
        self._token_blacklist.add(token_id, expires_at)
        self._logger.info(f"访问令牌已撤销并加入黑名单: {token_id}")
        
        # 同时撤销刷新令牌
        self.revoke_refresh_token(user_id, device_id)

    def extend_refresh_token(self, user_id: str, device_id: str, max_absolute_lifetime_days: int = 180) -> Result[bool]:
        """延长刷新令牌有效期（滑动过期机制）"""
        # 先检查黑名单
        token_id = f"{user_id}:{device_id}"
        if hasattr(self, '_token_blacklist') and self._token_blacklist.contains(token_id):
            self._logger.warning(f"访问令牌已经撤销: {token_id}")
            return Result.fail("访问令牌已经撤销")

        token_key = TokenClaims.get_refresh_token_key(user_id, device_id)
        token_claims = self._cache.get(token_key)
        
        if not token_claims:
            self._logger.warning(f"刷新令牌不存在: {user_id}:{device_id}")
            return Result.fail("刷新令牌不存在")
        
        # 获取当前时间
        now = get_current_timestamp()
        
        # 获取或设置首次颁发时间
        if not hasattr(token_claims, "first_issued_at") or token_claims.first_issued_at is None:
            token_claims.first_issued_at = token_claims.iat
        
        # 1. 先检查最大绝对有效期 - 调整顺序
        max_absolute_expiry = token_claims.first_issued_at + (max_absolute_lifetime_days * 86400)
        
        if now > max_absolute_expiry:
            self._logger.warning(f"刷新令牌已超过最大绝对有效期({max_absolute_lifetime_days}天)")
            return Result.fail(f"刷新令牌已超过最大有效期({max_absolute_lifetime_days}天)，请重新登录")
        
        # 2. 再检查是否已过期
        if now > token_claims.exp:
            self._logger.warning(f"刷新令牌已过期: {user_id}:{device_id}")
            return Result.fail("刷新令牌已过期")
        
        # 延长有效期，但不超过最大绝对有效期
        new_exp = now + (REFRESH_TOKEN_EXPIRE_DAYS * 86400)
        token_claims.exp = min(new_exp, max_absolute_expiry)
        self._cache.put(token_key, token_claims)
        
        self._logger.info(f"已延长刷新令牌有效期: {user_id}, 新过期时间: {datetime.fromtimestamp(token_claims.exp)}")
        return Result.ok(data=True, message="刷新令牌有效期已延长")
