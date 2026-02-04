"""统一的认证中间件"""

from typing import Optional, Tuple
from fastapi import Header, HTTPException

from app.core.config import settings
from app.core.logger import logger
from app.services.api_key_manager import api_key_manager
from app.models.api_key import APIKey


async def verify_api_key(authorization: Optional[str] = Header(None)) -> Tuple[bool, Optional[APIKey]]:
    """验证 API 密钥（统一认证入口）

    支持两种模式：
    1. 简单模式：使用配置文件中的单一 API_KEY（向后兼容）
    2. 多用户模式：使用 API Key 管理系统

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        (是否验证通过, APIKey对象或None)

    Raises:
        HTTPException: 认证失败时抛出
    """
    # 如果没有配置 API_KEY，则不需要认证
    if not settings.API_KEY and not await api_key_manager.list_keys():
        logger.debug("[Auth] 未配置认证，允许访问")
        return True, None

    # 检查 Authorization header
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization format. Use: Bearer <api_key>",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = authorization[7:]  # 移除 "Bearer " 前缀

    # 优先使用多用户模式
    keys = await api_key_manager.list_keys()
    if keys:
        # 多用户模式：验证 API Key
        is_valid, api_key, error_msg = await api_key_manager.validate_key(token)

        if not is_valid:
            logger.warning(f"[Auth] API Key 验证失败: {error_msg}")
            raise HTTPException(
                status_code=401 if not api_key else 429,
                detail=error_msg
            )

        logger.debug(f"[Auth] API Key 验证成功: {api_key.name}")
        return True, api_key

    # 简单模式：使用配置文件中的 API_KEY（向后兼容）
    if settings.API_KEY and token == settings.API_KEY:
        logger.debug("[Auth] 使用简单模式认证成功")
        return True, None

    logger.warning(f"[Auth] 认证失败: 无效的 API Key")
    raise HTTPException(
        status_code=401,
        detail="Invalid API key"
    )


async def get_sso_for_key(api_key: Optional[APIKey]) -> Optional[str]:
    """为 API Key 获取对应的 SSO Token

    如果 API Key 有专用的 SSO Token，则使用专用的；
    否则使用全局 SSO 池

    Args:
        api_key: APIKey 对象（可能为 None）

    Returns:
        SSO Token 或 None
    """
    if api_key and api_key.sso_tokens:
        # 使用专用 SSO Token（简单轮询）
        # TODO: 可以为专用 SSO 也实现轮询策略
        import random
        sso = random.choice(api_key.sso_tokens)
        logger.debug(f"[Auth] 使用专用 SSO: {api_key.name}")
        return sso

    # 使用全局 SSO 池
    from app.services.sso_manager import sso_manager
    sso = await sso_manager.get_next_sso()
    logger.debug(f"[Auth] 使用全局 SSO 池")
    return sso
