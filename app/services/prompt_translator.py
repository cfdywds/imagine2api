"""提示词翻译和优化服务"""

import re
import hashlib
from typing import Optional, Dict
import aiohttp
from app.core.config import settings
from app.core.logger import logger


class PromptTranslator:
    """提示词翻译器 - 将中文提示词翻译并优化为英文"""

    def __init__(self):
        self.cache: Dict[str, str] = {}  # 翻译缓存
        self.translation_prompt = """You are a professional prompt translator for AI image generation.

Task: Translate the following Chinese prompt to English and optimize it for AI image generation models like DALL-E, Midjourney, or Stable Diffusion.

Requirements:
1. Translate accurately while preserving the original meaning
2. Use descriptive, vivid language
3. Add relevant quality keywords (e.g., "high detail", "professional", "8k")
4. Add lighting and atmosphere descriptions if appropriate
5. Use comma-separated format
6. Keep it concise (under 200 words)

Chinese Prompt: {prompt}

Output only the optimized English prompt, without explanations."""

    def _get_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        return hashlib.md5(prompt.encode()).hexdigest()

    def detect_language(self, text: str) -> str:
        """
        检测文本语言

        Returns:
            'zh' - 中文
            'en' - 英文
        """
        # 检测是否包含中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        if chinese_pattern.search(text):
            return 'zh'
        return 'en'

    async def translate(
        self,
        prompt: str,
        enhance: bool = True,
        force: bool = False
    ) -> str:
        """
        翻译提示词

        Args:
            prompt: 原始提示词
            enhance: 是否增强提示词
            force: 是否强制翻译（忽略缓存）

        Returns:
            翻译后的提示词
        """
        # 检查是否启用翻译功能
        if not hasattr(settings, 'PROMPT_TRANSLATION_ENABLED') or not settings.PROMPT_TRANSLATION_ENABLED:
            logger.debug("[Translator] 提示词翻译功能未启用")
            return prompt

        # 去除首尾空格
        prompt = prompt.strip()

        # 检测语言
        language = self.detect_language(prompt)

        # 如果是英文，根据配置决定是否增强
        if language == 'en':
            logger.debug(f"[Translator] 检测到英文提示词，跳过翻译")
            if enhance and hasattr(settings, 'PROMPT_ENHANCEMENT_ENABLED') and settings.PROMPT_ENHANCEMENT_ENABLED:
                return await self._enhance_english_prompt(prompt)
            return prompt

        # 检查缓存
        cache_key = self._get_cache_key(prompt)
        if not force and cache_key in self.cache:
            logger.info(f"[Translator] 使用缓存的翻译结果")
            return self.cache[cache_key]

        # 调用 OpenAI API 翻译
        try:
            translated = await self._call_openai_api(prompt, enhance)

            # 缓存结果
            self.cache[cache_key] = translated

            logger.info(f"[Translator] 翻译成功")
            logger.debug(f"[Translator] 原文: {prompt}")
            logger.debug(f"[Translator] 译文: {translated}")

            return translated

        except Exception as e:
            logger.error(f"[Translator] 翻译失败: {e}")
            # 降级方案：返回原始提示词
            return prompt

    async def _call_openai_api(self, prompt: str, enhance: bool) -> str:
        """
        调用 OpenAI API 进行翻译

        Args:
            prompt: 原始中文提示词
            enhance: 是否增强

        Returns:
            翻译后的英文提示词
        """
        # 检查配置
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未配置")

        api_key = settings.OPENAI_API_KEY
        base_url = getattr(settings, 'OPENAI_BASE_URL', 'https://api.openai.com/v1')
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')

        # 构建请求
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 构建系统提示
        system_prompt = self.translation_prompt.format(prompt=prompt)

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": system_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        # 发送请求
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API 返回错误: {response.status} - {error_text}")

                result = await response.json()

                # 提取翻译结果
                translated = result['choices'][0]['message']['content'].strip()

                return translated

    async def _enhance_english_prompt(self, prompt: str) -> str:
        """
        增强英文提示词（添加质量关键词）

        Args:
            prompt: 英文提示词

        Returns:
            增强后的提示词
        """
        # 检查是否已经包含质量关键词
        quality_keywords = [
            'high detail', 'professional', '8k', '4k',
            'photorealistic', 'detailed', 'masterpiece'
        ]

        has_quality = any(keyword in prompt.lower() for keyword in quality_keywords)

        if has_quality:
            return prompt

        # 添加基础质量关键词
        return f"{prompt}, high detail, professional"

    def clear_cache(self):
        """清空翻译缓存"""
        self.cache.clear()
        logger.info("[Translator] 翻译缓存已清空")


# 全局翻译器实例
_translator: Optional[PromptTranslator] = None


def get_translator() -> PromptTranslator:
    """获取全局翻译器实例"""
    global _translator
    if _translator is None:
        _translator = PromptTranslator()
    return _translator
