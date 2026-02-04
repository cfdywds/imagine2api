"""测试中转站 API 连接"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.relay_client import RelayAPIClient
from app.core.logger import logger


async def test_relay_connection():
    """测试中转站连接"""
    print("=" * 60)
    print("测试中转站 API 连接")
    print("=" * 60)

    # 创建中转站客户端
    relay_client = RelayAPIClient(
        base_url="https://api.yexc.top/v1",
        api_key="sk-KxqASAFTrc4mkE1425v8W2mPZpWrSrPQqjhZm7cjpPA7yR0Q"
    )

    # 测试图片生成
    print("\n[1] 测试图片生成...")
    result = await relay_client.generate_image(
        prompt="a cute cat",
        model="dall-e-3",
        n=1,
        size="1024x1024"
    )

    if result.get("success"):
        print("[OK] 图片生成成功")
        data = result.get("data", {})
        images = data.get("data", [])
        print(f"  生成了 {len(images)} 张图片")
        for i, img in enumerate(images, 1):
            print(f"  图片 {i}: {img.get('url', 'N/A')}")
    else:
        print(f"[FAIL] 图片生成失败: {result.get('error')}")
        if result.get('details'):
            print(f"  详情: {result.get('details')}")

    # 测试 Chat Completions
    print("\n[2] 测试 Chat Completions...")
    result = await relay_client.chat_completion(
        messages=[
            {"role": "user", "content": "画一只小狗"}
        ],
        model="gpt-4",
        stream=False,
        n=1
    )

    if result.get("success"):
        print("[OK] Chat 成功")
        data = result.get("data", {})
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            print(f"  响应: {content[:100]}...")
    else:
        print(f"[FAIL] Chat 失败: {result.get('error')}")

    # 关闭客户端
    await relay_client.close()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_relay_connection())
