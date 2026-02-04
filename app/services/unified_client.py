"""统一的图片生成客户端 - 支持直连和中转站两种模式"""

from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logger import logger


async def generate_image(
    prompt: str,
    aspect_ratio: str = "2:3",
    n: int = 4,
    enable_nsfw: bool = True,
    sso: Optional[str] = None
) -> Dict[str, Any]:
    """
    统一的图片生成接口

    根据配置自动选择使用直连模式或中转站模式

    Args:
        prompt: 提示词
        aspect_ratio: 宽高比
        n: 生成数量
        enable_nsfw: 是否启用 NSFW
        sso: SSO Token（直连模式使用）

    Returns:
        生成结果
    """
    # 检查是否启用中转站模式
    if settings.RELAY_ENABLED:
        logger.info("[Client] 使用中转站模式")
        from app.services.relay_client import get_relay_client

        relay_client = get_relay_client()
        if relay_client is None:
            return {
                "success": False,
                "error": "中转站未配置",
                "error_code": "relay_not_configured"
            }

        # 转换 aspect_ratio 为 size
        size_map = {
            "1:1": "1024x1024",
            "2:3": "1024x1536",
            "3:2": "1536x1024",
            "16:9": "1792x1024",
            "9:16": "1024x1792"
        }
        size = size_map.get(aspect_ratio, "1024x1536")

        # 获取配置的模型名称
        model = settings.RELAY_IMAGE_MODEL

        # 调用中转站 API
        result = await relay_client.generate_image(
            prompt=prompt,
            model=model,
            n=n,
            size=size,
            response_format="url"
        )

        if result.get("success"):
            # 转换中转站响应格式为统一格式
            data = result.get("data", {})
            urls = [item.get("url") for item in data.get("data", [])]

            return {
                "success": True,
                "urls": urls,
                "count": len(urls),
                "mode": "relay"
            }
        else:
            return result

    else:
        # 使用直连模式
        logger.info("[Client] 使用直连模式")
        from app.services.grok_client import grok_client

        return await grok_client.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            n=n,
            enable_nsfw=enable_nsfw,
            sso=sso
        )


async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "grok-imagine",
    stream: bool = False,
    n: int = 1,
    aspect_ratio: str = "2:3"
) -> Dict[str, Any]:
    """
    统一的 Chat Completions 接口

    根据配置自动选择使用直连模式或中转站模式

    Args:
        messages: 消息列表
        model: 模型名称
        stream: 是否流式返回
        n: 生成数量
        aspect_ratio: 宽高比

    Returns:
        生成结果
    """
    # 检查是否启用中转站模式
    if settings.RELAY_ENABLED:
        logger.info("[Client] 使用中转站模式 (Chat)")
        from app.services.relay_client import get_relay_client

        relay_client = get_relay_client()
        if relay_client is None:
            return {
                "success": False,
                "error": "中转站未配置",
                "error_code": "relay_not_configured"
            }

        # 获取配置的模型名称
        model = settings.RELAY_CHAT_MODEL if hasattr(settings, 'RELAY_CHAT_MODEL') else "grok-4-fast"

        # 调用中转站 API
        result = await relay_client.chat_completion(
            messages=messages,
            model=model,
            stream=stream,
            n=n
        )

        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "mode": "relay"
            }
        else:
            return result

    else:
        # 使用直连模式
        logger.info("[Client] 使用直连模式 (Chat)")
        from app.services.grok_client import grok_client

        # 提取提示词
        prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                prompt = msg.get("content", "")
                break

        if not prompt:
            return {
                "success": False,
                "error": "未找到提示词",
                "error_code": "no_prompt"
            }

        # 调用直连生成
        result = await grok_client.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            n=n,
            enable_nsfw=True
        )

        return result
