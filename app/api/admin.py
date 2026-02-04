"""Admin API 路由"""

import asyncio
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logger import logger
from app.services.api_key_manager import api_key_manager

# 根据配置选择 SSO 管理器
if settings.REDIS_ENABLED:
    from app.services.redis_sso_manager import create_sso_manager
    sso_manager = create_sso_manager(
        use_redis=True,
        redis_url=settings.REDIS_URL,
        strategy=settings.SSO_ROTATION_STRATEGY,
        daily_limit=settings.SSO_DAILY_LIMIT
    )
else:
    from app.services.sso_manager import sso_manager

router = APIRouter()


# ============== API Key 管理请求模型 ==============

class CreateAPIKeyRequest(BaseModel):
    """创建 API Key 请求"""
    name: str = Field(..., description="API Key 名称", min_length=1, max_length=100)
    sso_tokens: Optional[List[str]] = Field(None, description="专用 SSO Token 列表（为空则使用全局池）")
    daily_limit: Optional[int] = Field(None, description="每日请求限制", ge=1)
    monthly_limit: Optional[int] = Field(None, description="每月请求限制", ge=1)
    note: str = Field("", description="备注")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API",
                "daily_limit": 100,
                "monthly_limit": 3000,
                "note": "生产环境使用"
            }
        }


class UpdateAPIKeyRequest(BaseModel):
    """更新 API Key 请求"""
    name: Optional[str] = Field(None, description="新名称")
    enabled: Optional[bool] = Field(None, description="是否启用")
    daily_limit: Optional[int] = Field(None, description="每日限制", ge=1)
    monthly_limit: Optional[int] = Field(None, description="每月限制", ge=1)
    note: Optional[str] = Field(None, description="备注")
    sso_tokens: Optional[List[str]] = Field(None, description="SSO Token 列表")


@router.get("/status")
async def get_status():
    """获取服务状态"""
    # Redis 版本是异步的
    if hasattr(sso_manager, 'get_status') and asyncio.iscoroutinefunction(sso_manager.get_status):
        sso_status = await sso_manager.get_status()
    else:
        sso_status = sso_manager.get_status()

    # 构建代理配置信息
    proxy_config = {
        "proxy_url": settings.PROXY_URL,
        "http_proxy": settings.HTTP_PROXY,
        "https_proxy": settings.HTTPS_PROXY
    }
    # 过滤掉 None 值
    proxy_config = {k: v for k, v in proxy_config.items() if v}

    return {
        "service": "running",
        "sso": sso_status,
        "proxy": proxy_config if proxy_config else "none",
        "config": {
            "host": settings.HOST,
            "port": settings.PORT,
            "images_dir": str(settings.IMAGES_DIR),
            "base_url": settings.get_base_url(),
            "sso_file": str(settings.SSO_FILE),
            "redis_enabled": settings.REDIS_ENABLED,
            "rotation_strategy": settings.SSO_ROTATION_STRATEGY,
            "daily_limit": settings.SSO_DAILY_LIMIT
        }
    }


@router.post("/sso/reload")
async def reload_sso():
    """重新加载 SSO 列表"""
    count = await sso_manager.reload()
    logger.info(f"[Admin] 重新加载 SSO: {count} 个")
    return {
        "success": True,
        "count": count
    }


@router.post("/sso/reset-usage")
async def reset_sso_usage():
    """手动重置每日使用量（仅 Redis 模式）"""
    if hasattr(sso_manager, 'reset_daily_usage'):
        await sso_manager.reset_daily_usage()
        logger.info("[Admin] 手动重置每日使用量")
        return {"success": True, "message": "每日使用量已重置"}
    return {"success": False, "message": "该功能仅在 Redis 模式下可用"}


@router.get("/images/list")
async def list_images(limit: int = 50):
    """列出已缓存的图片"""
    images = []
    if settings.IMAGES_DIR.exists():
        files = sorted(settings.IMAGES_DIR.glob("*.jpg"), key=lambda x: x.stat().st_mtime, reverse=True)
        for f in files[:limit]:
            images.append({
                "filename": f.name,
                "url": f"{settings.get_base_url()}/images/{f.name}",
                "size": f.stat().st_size
            })
    return {"images": images, "count": len(images)}


@router.delete("/images/clear")
async def clear_images():
    """清空图片缓存"""
    count = 0
    if settings.IMAGES_DIR.exists():
        for f in settings.IMAGES_DIR.glob("*"):
            if f.is_file():
                f.unlink()
                count += 1

    logger.info(f"[Admin] 已清空 {count} 张图片")
    return {"success": True, "deleted": count}


# ============== API Key 管理接口 ==============

@router.post("/api-keys")
async def create_api_key(request: CreateAPIKeyRequest):
    """创建新的 API Key

    支持为每个 API Key 配置：
    - 专用 SSO Token（可选）
    - 每日/每月请求限制
    - 备注信息
    """
    try:
        api_key = await api_key_manager.create_key(
            name=request.name,
            sso_tokens=request.sso_tokens,
            daily_limit=request.daily_limit,
            monthly_limit=request.monthly_limit,
            note=request.note
        )

        logger.info(f"[Admin] 创建 API Key: {api_key.name}")

        return {
            "success": True,
            "api_key": api_key.key,  # 完整的 key，只在创建时返回
            "masked_key": api_key.get_masked_key(),
            "name": api_key.name,
            "created_at": int(api_key.created_at),
            "message": "API Key 创建成功，请妥善保管，此密钥只显示一次"
        }
    except Exception as e:
        logger.error(f"[Admin] 创建 API Key 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-keys")
async def list_api_keys():
    """列出所有 API Keys（不包含完整密钥）"""
    keys = await api_key_manager.list_keys()

    return {
        "success": True,
        "count": len(keys),
        "keys": [key.get_status_dict() for key in keys]
    }


@router.get("/api-keys/{key}")
async def get_api_key_detail(key: str):
    """获取 API Key 详细信息"""
    api_key = await api_key_manager.get_key(key)

    if not api_key:
        raise HTTPException(status_code=404, detail="API Key 不存在")

    return {
        "success": True,
        "key": api_key.get_status_dict()
    }


@router.put("/api-keys/{key}")
async def update_api_key(key: str, request: UpdateAPIKeyRequest):
    """更新 API Key 配置"""
    success = await api_key_manager.update_key(
        key=key,
        name=request.name,
        enabled=request.enabled,
        daily_limit=request.daily_limit,
        monthly_limit=request.monthly_limit,
        note=request.note,
        sso_tokens=request.sso_tokens
    )

    if not success:
        raise HTTPException(status_code=404, detail="API Key 不存在")

    logger.info(f"[Admin] 更新 API Key: {key[:20]}...")

    return {
        "success": True,
        "message": "API Key 更新成功"
    }


@router.delete("/api-keys/{key}")
async def delete_api_key(key: str):
    """删除 API Key"""
    success = await api_key_manager.delete_key(key)

    if not success:
        raise HTTPException(status_code=404, detail="API Key 不存在")

    logger.info(f"[Admin] 删除 API Key: {key[:20]}...")

    return {
        "success": True,
        "message": "API Key 删除成功"
    }


@router.get("/api-keys-stats")
async def get_api_keys_statistics():
    """获取 API Keys 整体统计信息"""
    stats = await api_key_manager.get_statistics()

    return {
        "success": True,
        "statistics": stats
    }
