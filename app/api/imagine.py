"""Imagine API 路由 - OpenAI 兼容格式，支持流式预览"""

import time
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import base64
from PIL import Image
import io

from app.core.config import settings
from app.core.logger import logger
from app.services.grok_client import grok_client
from app.middleware.auth import verify_api_key, get_sso_for_key
from app.services.api_key_manager import api_key_manager
from app.services import unified_client


router = APIRouter()


# ============== 请求/响应模型 ==============

class OpenAIImageRequest(BaseModel):
    """OpenAI 兼容的图片生成请求"""
    prompt: str = Field(..., description="图片描述提示词", min_length=1)
    model: Optional[str] = Field("grok-2-image", description="模型名称")
    n: Optional[int] = Field(4, description="生成数量", ge=1, le=4)
    size: Optional[str] = Field("1024x1536", description="图片尺寸")
    response_format: Optional[str] = Field("url", description="响应格式: url 或 b64_json")
    stream: Optional[bool] = Field(False, description="是否流式返回进度")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "a beautiful sunset over the ocean",
                "n": 2,
                "size": "1024x1536"
            }
        }


class OpenAIImageData(BaseModel):
    """OpenAI 格式的图片数据"""
    url: Optional[str] = None
    b64_json: Optional[str] = None


class OpenAIImageResponse(BaseModel):
    """OpenAI 兼容的图片响应"""
    created: int
    data: List[OpenAIImageData]


# ============== 辅助函数 ==============

def size_to_aspect_ratio(size: str) -> str:
    """将 OpenAI 的 size 转换为 aspect_ratio"""
    size_map = {
        "1024x1024": "1:1",
        "1024x1536": "2:3",
        "1536x1024": "3:2",
        "512x512": "1:1",
        "256x256": "1:1",
    }
    return size_map.get(size, "2:3")


# ============== API 路由 ==============

@router.post("/images/generations", response_model=OpenAIImageResponse)
async def generate_image(
    request: OpenAIImageRequest,
    authorization: Optional[str] = Header(None)
):
    """
    生成图片 (OpenAI 兼容 API)

    支持两种模式:
    - stream=false (默认): 返回完整结果
    - stream=true: 流式返回生成进度 (SSE 格式)
    """
    # 验证 API Key
    is_valid, api_key = await verify_api_key(authorization)

    logger.info(f"[API] 生成请求: {request.prompt[:50]}... stream={request.stream}")

    aspect_ratio = size_to_aspect_ratio(request.size)

    # 检查是否使用中转站模式
    if settings.RELAY_ENABLED:
        logger.info("[API] 使用中转站模式")

        # 使用统一客户端（中转站模式）
        result = await unified_client.generate_image(
            prompt=request.prompt,
            aspect_ratio=aspect_ratio,
            n=request.n,
            enable_nsfw=True
        )

        # 记录使用
        if api_key:
            await api_key_manager.record_usage(api_key.key)

        if not result.get("success"):
            error_msg = result.get("error", "Image generation failed")
            error_code = result.get("error_code", "")

            if error_code == "rate_limit_exceeded":
                raise HTTPException(status_code=429, detail=error_msg)
            else:
                raise HTTPException(status_code=500, detail=error_msg)

        # 严格按照 response_format 返回
        if request.response_format == "b64_json":
            # 返回 base64 格式
            b64_list = result.get("b64_list", [])
            data = [OpenAIImageData(b64_json=b64) for b64 in b64_list]
        else:
            # 返回 URL 格式
            data = [OpenAIImageData(url=url) for url in result.get("urls", [])]

        return OpenAIImageResponse(
            created=int(time.time()),
            data=data
        )

    # 直连模式（原有逻辑）
    logger.info("[API] 使用直连模式")

    # 获取对应的 SSO Token
    sso = await get_sso_for_key(api_key)

    # 流式模式
    if request.stream:
        return StreamingResponse(
            stream_generate(
                prompt=request.prompt,
                aspect_ratio=aspect_ratio,
                n=request.n,
                sso=sso,
                api_key=api_key
            ),
            media_type="text/event-stream"
        )

    # 普通模式
    result = await grok_client.generate(
        prompt=request.prompt,
        aspect_ratio=aspect_ratio,
        n=request.n,
        enable_nsfw=True,
        sso=sso
    )

    # 记录使用
    if api_key:
        await api_key_manager.record_usage(api_key.key)

    if not result.get("success"):
        error_msg = result.get("error", "Image generation failed")
        error_code = result.get("error_code", "")

        if error_code == "rate_limit_exceeded":
            raise HTTPException(status_code=429, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    # 严格按照 response_format 返回
    if request.response_format == "b64_json":
        # 返回 base64 格式
        b64_list = result.get("b64_list", [])
        data = [OpenAIImageData(b64_json=b64) for b64 in b64_list]
    else:
        # 返回 URL 格式
        data = [OpenAIImageData(url=url) for url in result.get("urls", [])]

    return OpenAIImageResponse(
        created=int(time.time()),
        data=data
    )


async def stream_generate(prompt: str, aspect_ratio: str, n: int, sso: Optional[str] = None, api_key=None):
    """
    流式生成图片

    SSE 格式输出:
    - event: progress - 生成进度更新
    - event: complete - 生成完成，包含最终 URL
    - event: error - 发生错误
    """
    try:
        async for item in grok_client.generate_stream(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            n=n,
            enable_nsfw=True,
            sso=sso
        ):
            if item.get("type") == "progress":
                # 进度更新
                event_data = {
                    "image_id": item["image_id"],
                    "stage": item["stage"],
                    "is_final": item["is_final"],
                    "completed": item["completed"],
                    "total": item["total"],
                    "progress": f"{item['completed']}/{item['total']}"
                }
                yield f"event: progress\ndata: {json.dumps(event_data)}\n\n"

            elif item.get("type") == "result":
                # 最终结果
                if item.get("success"):
                    # 记录使用
                    if api_key:
                        await api_key_manager.record_usage(api_key.key)

                    result_data = {
                        "created": int(time.time()),
                        "data": [{"url": url} for url in item.get("urls", [])]
                    }
                    yield f"event: complete\ndata: {json.dumps(result_data)}\n\n"
                else:
                    error_data = {"error": item.get("error", "Generation failed")}
                    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
                break

    except Exception as e:
        logger.error(f"[API] 流式生成错误: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get("/models/imagine")
async def list_imagine_models():
    """列出图片生成模型"""
    return {
        "object": "list",
        "data": [
            {
                "id": "grok-imagine",
                "object": "model",
                "created": 1700000000,
                "owned_by": "xai"
            }
        ]
    }


@router.post("/images/edit")
async def edit_image(
    prompt: str = Form(..., description="文本提示词"),
    image: UploadFile = File(..., description="上传的图片"),
    mode: str = Form("style_transfer", description="生成模式"),
    strength: float = Form(0.8, ge=0.0, le=1.0, description="变化强度"),
    aspect_ratio: str = Form("1:1", description="宽高比"),
    authorization: Optional[str] = Header(None)
):
    """
    图生图 API

    支持的模式：
    - style_transfer: 风格迁移
    - upscale: 图片放大
    - inpainting: 图片修复
    - background_replace: 背景替换
    """
    # 验证 API Key
    is_valid, api_key = await verify_api_key(authorization)

    # 获取对应的 SSO Token
    sso = await get_sso_for_key(api_key)

    # 读取图片
    contents = await image.read()

    # 压缩图片
    try:
        img = Image.open(io.BytesIO(contents))

        # 转换为 RGB（如果是 RGBA 或其他格式）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # 限制最大尺寸为 1024x1024
        max_size = (1024, 1024)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # 压缩为 JPEG，质量 85
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        compressed_data = output.getvalue()

        # 如果压缩后仍然太大（> 500KB），降低质量
        if len(compressed_data) > 500 * 1024:
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=70, optimize=True)
            compressed_data = output.getvalue()

        logger.info(f"[API] 图片压缩: {len(contents)} -> {len(compressed_data)} bytes ({len(compressed_data)/len(contents)*100:.1f}%)")

        # 使用压缩后的数据
        image_base64 = base64.b64encode(compressed_data).decode()

    except Exception as e:
        logger.error(f"[API] 图片压缩失败: {e}")
        # 如果压缩失败，使用原始图片
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图片大小不能超过 10MB")
        image_base64 = base64.b64encode(contents).decode()

    # 验证图片格式
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只支持图片文件")

    logger.info(f"[API] 图生图请求: {prompt[:50]}... mode={mode}, size={len(contents)} bytes")

    # 调用生成
    result = await grok_client.generate_image_to_image(
        prompt=prompt,
        image_base64=image_base64,
        aspect_ratio=aspect_ratio,
        mode=mode,
        strength=strength,
        enable_nsfw=True,
        sso=sso
    )

    if not result.get("success"):
        error_msg = result.get("error", "图生图失败")
        error_code = result.get("error_code", "")

        if error_code == "rate_limit_exceeded":
            raise HTTPException(status_code=429, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    # 记录使用
    if api_key:
        await api_key_manager.record_usage(api_key.key)

    return {
        "created": int(time.time()),
        "data": [{"url": url} for url in result.get("urls", [])]
    }

