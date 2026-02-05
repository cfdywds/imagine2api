"""
动态代理服务
支持从星空代理 API 自动获取和更新代理
"""

import asyncio
import time
from typing import Optional
from datetime import datetime, timedelta
import aiohttp
from app.core.logger import logger


class DynamicProxyManager:
    """动态代理管理器"""

    def __init__(self, api_url: str, refresh_interval: int = 300):
        """
        初始化动态代理管理器

        Args:
            api_url: 代理 API 地址
            refresh_interval: 代理刷新间隔（秒），默认 5 分钟
        """
        self.api_url = api_url
        self.refresh_interval = refresh_interval
        self.current_proxy: Optional[str] = None
        self.last_refresh: Optional[datetime] = None
        self._refresh_task: Optional[asyncio.Task] = None

    async def fetch_proxy(self) -> Optional[str]:
        """从 API 获取代理地址"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        content = content.strip()

                        # 检查是否是错误响应
                        if content.startswith('{'):
                            logger.error(f"代理 API 返回错误: {content}")
                            return None

                        # 添加协议前缀
                        if not content.startswith(('http://', 'https://', 'socks5://')):
                            proxy_url = f"http://{content}"
                        else:
                            proxy_url = content

                        logger.info(f"获取到新代理: {proxy_url}")
                        return proxy_url
                    else:
                        logger.error(f"获取代理失败: HTTP {response.status}")
                        return None

        except Exception as e:
            logger.error(f"获取代理异常: {e}")
            return None

    async def refresh_proxy(self) -> bool:
        """刷新代理"""
        new_proxy = await self.fetch_proxy()

        if new_proxy:
            self.current_proxy = new_proxy
            self.last_refresh = datetime.now()
            logger.info(f"代理已更新: {new_proxy}")
            return True
        else:
            logger.warning("代理刷新失败，继续使用旧代理")
            return False

    async def get_proxy(self) -> Optional[str]:
        """获取当前可用的代理"""
        # 如果没有代理或代理已过期，刷新
        if not self.current_proxy or self._should_refresh():
            await self.refresh_proxy()

        return self.current_proxy

    def _should_refresh(self) -> bool:
        """判断是否需要刷新代理"""
        if not self.last_refresh:
            return True

        elapsed = (datetime.now() - self.last_refresh).total_seconds()
        return elapsed >= self.refresh_interval

    async def start_auto_refresh(self):
        """启动自动刷新任务"""
        if self._refresh_task and not self._refresh_task.done():
            logger.warning("自动刷新任务已在运行")
            return

        logger.info(f"启动代理自动刷新任务 (间隔: {self.refresh_interval}秒)")
        self._refresh_task = asyncio.create_task(self._auto_refresh_loop())

    async def _auto_refresh_loop(self):
        """自动刷新循环"""
        while True:
            try:
                await asyncio.sleep(self.refresh_interval)
                await self.refresh_proxy()
            except asyncio.CancelledError:
                logger.info("代理自动刷新任务已停止")
                break
            except Exception as e:
                logger.error(f"自动刷新异常: {e}")

    async def stop_auto_refresh(self):
        """停止自动刷新任务"""
        if self._refresh_task and not self._refresh_task.done():
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            logger.info("代理自动刷新任务已停止")


# 全局代理管理器实例（可选）
_proxy_manager: Optional[DynamicProxyManager] = None


def init_dynamic_proxy(api_url: str, refresh_interval: int = 300) -> DynamicProxyManager:
    """初始化全局动态代理管理器"""
    global _proxy_manager
    _proxy_manager = DynamicProxyManager(api_url, refresh_interval)
    return _proxy_manager


def get_proxy_manager() -> Optional[DynamicProxyManager]:
    """获取全局代理管理器"""
    return _proxy_manager
