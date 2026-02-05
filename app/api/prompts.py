"""提示词翻译 API"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.middleware.auth import verify_api_key
from app.services.prompt_translator import get_translator


router = APIRouter()


# ============== 请求/响应模型 ==============

class TranslateRequest(BaseModel):
    """翻译请求"""
    prompt: str = Field(..., description="要翻译的提示词")
    enhance: bool = Field(True, description="是否增强提示词")
    force: bool = Field(False, description="是否强制翻译（忽略缓存）")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "画一只可爱的猫咪，坐在窗台上晒太阳",
                "enhance": True,
                "force": False
            }
        }


class TranslateResponse(BaseModel):
    """翻译响应"""
    original: str = Field(..., description="原始提示词")
    translated: str = Field(..., description="翻译后的提示词")
    language: str = Field(..., description="检测到的语言 (zh/en)")
    enhanced: bool = Field(..., description="是否进行了增强")
    cached: bool = Field(..., description="是否使用了缓存")


# ============== API 路由 ==============

@router.post("/prompts/translate", response_model=TranslateResponse)
async def translate_prompt(
    request: TranslateRequest,
    authorization: Optional[str] = Header(None)
):
    """
    翻译提示词接口

    将中文提示词翻译并优化为英文，用户可以预览翻译结果
    """
    # 验证 API Key
    is_valid, api_key = await verify_api_key(authorization)

    logger.info(f"[Translate] 翻译请求: {request.prompt[:50]}...")

    # 获取翻译器
    translator = get_translator()

    # 检测语言
    language = translator.detect_language(request.prompt)

    # 检查缓存
    cache_key = translator._get_cache_key(request.prompt)
    cached = cache_key in translator.cache and not request.force

    # 翻译
    try:
        translated = await translator.translate(
            request.prompt,
            enhance=request.enhance,
            force=request.force
        )

        # 判断是否进行了增强
        enhanced = translated != request.prompt and request.enhance

        logger.info(f"[Translate] 翻译成功 (cached={cached})")

        return TranslateResponse(
            original=request.prompt,
            translated=translated,
            language=language,
            enhanced=enhanced,
            cached=cached
        )

    except Exception as e:
        logger.error(f"[Translate] 翻译失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/prompts/clear-cache")
async def clear_translation_cache(
    authorization: Optional[str] = Header(None)
):
    """
    清空翻译缓存

    需要管理员权限
    """
    # 验证 API Key
    is_valid, api_key = await verify_api_key(authorization)

    # 获取翻译器
    translator = get_translator()

    # 清空缓存
    cache_size = len(translator.cache)
    translator.clear_cache()

    logger.info(f"[Translate] 清空缓存，共 {cache_size} 条记录")

    return {
        "success": True,
        "message": f"Cache cleared, {cache_size} entries removed"
    }


@router.get("/prompts/cache-stats")
async def get_cache_stats(
    authorization: Optional[str] = Header(None)
):
    """
    获取缓存统计信息
    """
    # 验证 API Key
    is_valid, api_key = await verify_api_key(authorization)

    # 获取翻译器
    translator = get_translator()

    return {
        "cache_size": len(translator.cache),
        "cache_entries": list(translator.cache.keys())[:10]  # 只返回前10条
    }
