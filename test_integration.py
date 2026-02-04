"""测试完整的中转站集成"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.logger import logger


async def test_integration():
    """测试中转站集成"""
    print("=" * 60)
    print("测试中转站集成")
    print("=" * 60)

    # 1. 检查配置
    print("\n[1] 检查配置...")
    print(f"  RELAY_ENABLED: {settings.RELAY_ENABLED}")
    print(f"  RELAY_BASE_URL: {settings.RELAY_BASE_URL}")
    print(f"  RELAY_API_KEY: {settings.RELAY_API_KEY[:20]}..." if settings.RELAY_API_KEY else "  RELAY_API_KEY: (未配置)")

    if hasattr(settings, 'RELAY_CHAT_MODEL'):
        print(f"  RELAY_CHAT_MODEL: {settings.RELAY_CHAT_MODEL}")
    if hasattr(settings, 'RELAY_IMAGE_MODEL'):
        print(f"  RELAY_IMAGE_MODEL: {settings.RELAY_IMAGE_MODEL}")

    if not settings.RELAY_ENABLED:
        print("\n[提示] 中转站模式未启用")
        print("  请在 .env 文件中设置 RELAY_ENABLED=true")
        return

    # 2. 测试中转站客户端
    print("\n[2] 测试中转站客户端...")
    from app.services.relay_client import RelayAPIClient

    client = RelayAPIClient(
        base_url=settings.RELAY_BASE_URL,
        api_key=settings.RELAY_API_KEY
    )

    # 测试 Chat
    print("\n  测试 Chat Completions...")
    result = await client.chat_completion(
        messages=[{"role": "user", "content": "Hello"}],
        model="grok-4-fast",
        stream=False
    )

    if result.get("success"):
        print("  [OK] Chat 测试成功")
        data = result.get("data", {})
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            print(f"  回复: {content[:100]}...")
    else:
        print(f"  [FAIL] Chat 测试失败: {result.get('error')}")

    await client.close()

    # 3. 测试统一客户端
    print("\n[3] 测试统一客户端...")
    from app.services.unified_client import chat_completion

    result = await chat_completion(
        messages=[{"role": "user", "content": "你好"}],
        model="grok-4-fast",
        stream=False
    )

    if result.get("success"):
        print("  [OK] 统一客户端测试成功")
        print(f"  模式: {result.get('mode', 'unknown')}")
    else:
        print(f"  [FAIL] 统一客户端测试失败: {result.get('error')}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    # 总结
    print("\n总结:")
    if settings.RELAY_ENABLED:
        print("  ✓ 中转站模式已启用")
        print("  ✓ Chat 功能可用")
        print("\n下一步:")
        print("  1. 启动服务: python main.py")
        print("  2. 测试接口: curl -X POST http://localhost:9563/v1/chat/completions ...")
        print("  3. 查看文档: 中转站集成完成.md")
    else:
        print("  ✗ 中转站模式未启用")
        print("\n启用方法:")
        print("  1. 编辑 .env 文件")
        print("  2. 设置 RELAY_ENABLED=true")
        print("  3. 重新运行此测试")


if __name__ == "__main__":
    asyncio.run(test_integration())
