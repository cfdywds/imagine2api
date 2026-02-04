"""API Key 管理服务"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from app.core.config import settings
from app.core.logger import logger
from app.models.api_key import APIKey, generate_api_key


class APIKeyManager:
    """API Key 管理器

    功能：
    1. 创建、删除、查询 API Key
    2. 验证 API Key
    3. 跟踪使用统计
    4. 配额管理
    5. 持久化到 JSON 文件
    """

    RESET_DAILY_INTERVAL = 86400  # 24小时
    RESET_MONTHLY_INTERVAL = 2592000  # 30天

    def __init__(self, storage_file: Optional[Path] = None):
        self._storage_file = storage_file or (settings.SSO_FILE.parent / "api_keys.json")
        self._keys: Dict[str, APIKey] = {}  # key -> APIKey
        self._lock = asyncio.Lock()
        self._load_keys()

    def _load_keys(self):
        """从文件加载 API Keys"""
        if not self._storage_file.exists():
            logger.info("[APIKey] 存储文件不存在，将创建新文件")
            return

        try:
            with open(self._storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key_data in data.get("keys", []):
                api_key = APIKey.from_dict(key_data)
                self._keys[api_key.key] = api_key

            logger.info(f"[APIKey] 已加载 {len(self._keys)} 个 API Key")
        except Exception as e:
            logger.error(f"[APIKey] 加载失败: {e}")

    def _save_keys(self):
        """保存 API Keys 到文件"""
        try:
            # 确保目录存在
            self._storage_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0",
                "updated_at": time.time(),
                "keys": [key.to_dict() for key in self._keys.values()]
            }

            with open(self._storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"[APIKey] 已保存 {len(self._keys)} 个 API Key")
        except Exception as e:
            logger.error(f"[APIKey] 保存失败: {e}")

    async def create_key(
        self,
        name: str,
        sso_tokens: Optional[List[str]] = None,
        daily_limit: Optional[int] = None,
        monthly_limit: Optional[int] = None,
        note: str = ""
    ) -> APIKey:
        """创建新的 API Key

        Args:
            name: 用户友好的名称
            sso_tokens: 专用 SSO Token 列表（为空则使用全局池）
            daily_limit: 每日请求限制
            monthly_limit: 每月请求限制
            note: 备注

        Returns:
            创建的 APIKey 对象
        """
        async with self._lock:
            # 生成唯一的 key
            while True:
                key = generate_api_key()
                if key not in self._keys:
                    break

            api_key = APIKey(
                key=key,
                name=name,
                sso_tokens=sso_tokens or [],
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                note=note
            )

            self._keys[key] = api_key
            self._save_keys()

            logger.info(f"[APIKey] 创建新 Key: {name} ({api_key.get_masked_key()})")
            return api_key

    async def delete_key(self, key: str) -> bool:
        """删除 API Key

        Args:
            key: 要删除的 API Key

        Returns:
            是否删除成功
        """
        async with self._lock:
            if key in self._keys:
                api_key = self._keys[key]
                del self._keys[key]
                self._save_keys()
                logger.info(f"[APIKey] 删除 Key: {api_key.name} ({api_key.get_masked_key()})")
                return True
            return False

    async def get_key(self, key: str) -> Optional[APIKey]:
        """获取 API Key 对象

        Args:
            key: API Key

        Returns:
            APIKey 对象，不存在则返回 None
        """
        return self._keys.get(key)

    async def list_keys(self) -> List[APIKey]:
        """列出所有 API Keys

        Returns:
            API Key 列表
        """
        return list(self._keys.values())

    async def validate_key(self, key: str) -> tuple[bool, Optional[APIKey], str]:
        """验证 API Key

        Args:
            key: 要验证的 API Key

        Returns:
            (是否有效, APIKey对象, 错误信息)
        """
        api_key = await self.get_key(key)

        if not api_key:
            return False, None, "无效的 API Key"

        # 检查配额
        can_use, error_msg = api_key.check_quota()
        if not can_use:
            return False, api_key, error_msg

        # 检查是否需要重置统计
        await self._check_reset(api_key)

        return True, api_key, ""

    async def record_usage(self, key: str):
        """记录 API Key 使用

        Args:
            key: API Key
        """
        async with self._lock:
            api_key = self._keys.get(key)
            if api_key:
                api_key.record_usage()
                self._save_keys()

    async def update_key(
        self,
        key: str,
        name: Optional[str] = None,
        enabled: Optional[bool] = None,
        daily_limit: Optional[int] = None,
        monthly_limit: Optional[int] = None,
        note: Optional[str] = None,
        sso_tokens: Optional[List[str]] = None
    ) -> bool:
        """更新 API Key 配置

        Args:
            key: API Key
            name: 新名称
            enabled: 是否启用
            daily_limit: 每日限制
            monthly_limit: 每月限制
            note: 备注
            sso_tokens: SSO Token 列表

        Returns:
            是否更新成功
        """
        async with self._lock:
            api_key = self._keys.get(key)
            if not api_key:
                return False

            if name is not None:
                api_key.name = name
            if enabled is not None:
                api_key.enabled = enabled
            if daily_limit is not None:
                api_key.daily_limit = daily_limit
            if monthly_limit is not None:
                api_key.monthly_limit = monthly_limit
            if note is not None:
                api_key.note = note
            if sso_tokens is not None:
                api_key.sso_tokens = sso_tokens

            self._save_keys()
            logger.info(f"[APIKey] 更新 Key: {api_key.name} ({api_key.get_masked_key()})")
            return True

    async def _check_reset(self, api_key: APIKey):
        """检查是否需要重置统计"""
        now = time.time()

        # 每日重置
        if now - api_key.last_reset_daily >= self.RESET_DAILY_INTERVAL:
            api_key.reset_daily()
            logger.info(f"[APIKey] 重置每日统计: {api_key.name}")

        # 每月重置
        if now - api_key.last_reset_monthly >= self.RESET_MONTHLY_INTERVAL:
            api_key.reset_monthly()
            logger.info(f"[APIKey] 重置每月统计: {api_key.name}")

    async def get_statistics(self) -> dict:
        """获取整体统计信息

        Returns:
            统计信息字典
        """
        total_keys = len(self._keys)
        enabled_keys = sum(1 for k in self._keys.values() if k.enabled)
        total_requests = sum(k.total_requests for k in self._keys.values())

        return {
            "total_keys": total_keys,
            "enabled_keys": enabled_keys,
            "disabled_keys": total_keys - enabled_keys,
            "total_requests": total_requests,
            "keys_with_dedicated_sso": sum(1 for k in self._keys.values() if k.sso_tokens)
        }


# 全局实例
api_key_manager = APIKeyManager()
