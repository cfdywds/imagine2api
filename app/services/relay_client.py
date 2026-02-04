"""中转站 API 客户端 - 通过 HTTP API 调用中转站服务"""

import aiohttp
import asyncio
import time
import base64
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.core.logger import logger


class RelayAPIClient:
    """中转站 API 客户端

    通过 HTTP API 调用中转站，而不是直接使用 Grok WebSocket
    """

    def __init__(self, base_url: str, api_key: str):
        """
        初始化中转站客户端

        Args:
            base_url: 中转站 API 地址（如：https://api.yexc.top/v1）
            api_key: 中转站 API Key
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=180, connect=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_image(
        self,
        prompt: str,
        n: int = 1,
        size: str = "1024x1536",
        response_format: str = "url",
        model: str = "dall-e-3"
    ) -> Dict[str, Any]:
        """
        生成图片（OpenAI 格式）

        Args:
            prompt: 提示词
            n: 生成数量
            size: 图片尺寸
            response_format: 响应格式（url 或 b64_json）
            model: 模型名称（默认 dall-e-3）

        Returns:
            生成结果
        """
        url = f"{self.base_url}/images/generations"

        payload = {
            "prompt": prompt,
            "model": model,
            "n": n,
            "size": size,
            "response_format": response_format
        }

        logger.info(f"[Relay] 调用中转站生成图片: {prompt[:50]}... model={model}, n={n}")

        try:
            session = await self._get_session()
            async with session.post(url, json=payload, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"[Relay] 生成成功，返回 {len(data.get('data', []))} 张图片")
                    return {
                        "success": True,
                        "data": data
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"[Relay] 生成失败: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"中转站返回错误: {response.status}",
                        "error_code": "relay_error",
                        "details": error_text
                    }

        except asyncio.TimeoutError:
            logger.error("[Relay] 请求超时")
            return {
                "success": False,
                "error": "请求超时",
                "error_code": "timeout"
            }
        except Exception as e:
            logger.error(f"[Relay] 请求失败: {e}")
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "error_code": "request_error"
            }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "grok-imagine",
        stream: bool = False,
        n: int = 1
    ) -> Dict[str, Any]:
        """
        Chat Completions（OpenAI 格式）

        Args:
            messages: 消息列表
            model: 模型名称
            stream: 是否流式返回
            n: 生成数量

        Returns:
            生成结果
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "n": n
        }

        logger.info(f"[Relay] 调用中转站 Chat: model={model}, stream={stream}")

        try:
            session = await self._get_session()
            async with session.post(url, json=payload, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"[Relay] Chat 成功")
                    return {
                        "success": True,
                        "data": data
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"[Relay] Chat 失败: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"中转站返回错误: {response.status}",
                        "error_code": "relay_error"
                    }

        except asyncio.TimeoutError:
            logger.error("[Relay] 请求超时")
            return {
                "success": False,
                "error": "请求超时",
                "error_code": "timeout"
            }
        except Exception as e:
            logger.error(f"[Relay] 请求失败: {e}")
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "error_code": "request_error"
            }

    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()


# 全局中转站客户端实例（如果配置了中转站）
relay_client: Optional[RelayAPIClient] = None

def get_relay_client() -> Optional[RelayAPIClient]:
    """获取中转站客户端实例"""
    global relay_client

    # 检查是否配置了中转站
    if hasattr(settings, 'RELAY_ENABLED') and settings.RELAY_ENABLED:
        if relay_client is None:
            relay_client = RelayAPIClient(
                base_url=settings.RELAY_BASE_URL,
                api_key=settings.RELAY_API_KEY
            )
        return relay_client

    return None
