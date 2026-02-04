"""API Key 数据模型"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime
import time
import secrets
import hashlib


@dataclass
class APIKey:
    """API Key 模型"""
    key: str  # API Key (sk-xxx 格式)
    name: str  # 用户友好的名称
    created_at: float = field(default_factory=time.time)

    # SSO 配置
    sso_tokens: List[str] = field(default_factory=list)  # 专用 SSO Token 列表（为空则使用全局池）

    # 配额限制
    daily_limit: Optional[int] = None  # 每日请求限制（None 表示无限制）
    monthly_limit: Optional[int] = None  # 每月请求限制

    # 使用统计
    total_requests: int = 0  # 总请求数
    daily_requests: int = 0  # 今日请求数
    monthly_requests: int = 0  # 本月请求数
    last_used_at: float = 0  # 最后使用时间
    last_reset_daily: float = field(default_factory=time.time)  # 上次每日重置时间
    last_reset_monthly: float = field(default_factory=time.time)  # 上次每月重置时间

    # 状态
    enabled: bool = True  # 是否启用
    note: str = ""  # 备注

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "APIKey":
        """从字典创建"""
        return cls(**data)

    def get_key_hash(self) -> str:
        """获取 Key 的哈希值（用于显示）"""
        return hashlib.sha256(self.key.encode()).hexdigest()[:12]

    def get_masked_key(self) -> str:
        """获取脱敏的 Key"""
        if len(self.key) <= 12:
            return self.key[:4] + "..." + self.key[-4:]
        return self.key[:8] + "..." + self.key[-4:]

    def check_quota(self) -> tuple[bool, str]:
        """检查配额是否可用

        Returns:
            (是否可用, 错误信息)
        """
        if not self.enabled:
            return False, "API Key 已禁用"

        if self.daily_limit and self.daily_requests >= self.daily_limit:
            return False, f"已达到每日请求限制 ({self.daily_limit})"

        if self.monthly_limit and self.monthly_requests >= self.monthly_limit:
            return False, f"已达到每月请求限制 ({self.monthly_limit})"

        return True, ""

    def record_usage(self):
        """记录一次使用"""
        self.total_requests += 1
        self.daily_requests += 1
        self.monthly_requests += 1
        self.last_used_at = time.time()

    def reset_daily(self):
        """重置每日统计"""
        self.daily_requests = 0
        self.last_reset_daily = time.time()

    def reset_monthly(self):
        """重置每月统计"""
        self.monthly_requests = 0
        self.last_reset_monthly = time.time()

    def get_status_dict(self) -> dict:
        """获取状态信息（用于 API 返回）"""
        return {
            "key": self.get_masked_key(),
            "name": self.name,
            "enabled": self.enabled,
            "created_at": int(self.created_at),
            "last_used_at": int(self.last_used_at) if self.last_used_at else None,
            "has_dedicated_sso": len(self.sso_tokens) > 0,
            "sso_count": len(self.sso_tokens),
            "usage": {
                "total": self.total_requests,
                "daily": self.daily_requests,
                "monthly": self.monthly_requests,
                "daily_limit": self.daily_limit,
                "monthly_limit": self.monthly_limit,
                "daily_remaining": (self.daily_limit - self.daily_requests) if self.daily_limit else None,
                "monthly_remaining": (self.monthly_limit - self.monthly_requests) if self.monthly_limit else None,
            },
            "note": self.note
        }


def generate_api_key(prefix: str = "sk") -> str:
    """生成新的 API Key

    格式: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (32位随机字符)
    """
    random_part = secrets.token_urlsafe(24)  # 生成 32 个字符
    return f"{prefix}-{random_part}"
