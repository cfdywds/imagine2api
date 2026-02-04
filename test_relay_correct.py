"""测试中转站 - 使用正确的模型名称"""

import asyncio
import aiohttp


async def test_with_correct_model():
    """使用正确的模型名称测试"""
    base_url = "https://api.yexc.top/v1"
    api_key = "sk-KxqASAFTrc4mkE1425v8W2mPZpWrSrPQqjhZm7cjpPA7yR0Q"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("=" * 60)
    print("测试中转站 - 使用正确的模型")
    print("=" * 60)

    # 1. 测试图片生成 - 使用 grok-imagine-0.9
    print("\n[1] 测试图片生成 (grok-imagine-0.9)...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "grok-imagine-0.9",
                "prompt": "a cute cat",
                "n": 1,
                "size": "1024x1024"
            }
            async with session.post(
                f"{base_url}/images/generations",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                print(f"  状态码: {response.status}")
                text = await response.text()
                print(f"  响应: {text[:500]}")

                if response.status == 200:
                    data = await response.json()
                    print(f"  [OK] 成功！")
                    images = data.get("data", [])
                    for i, img in enumerate(images, 1):
                        print(f"    图片 {i}: {img.get('url', 'N/A')}")
                else:
                    print(f"  [FAIL] 失败")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # 2. 测试 Chat - 使用 grok-4-fast
    print("\n[2] 测试 Chat Completions (grok-4-fast)...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "grok-4-fast",
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "stream": False
            }
            async with session.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                print(f"  状态码: {response.status}")
                text = await response.text()
                print(f"  响应: {text[:500]}")

                if response.status == 200:
                    data = await response.json()
                    print(f"  [OK] 成功！")
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        print(f"    回复: {content[:100]}")
                else:
                    print(f"  [FAIL] 失败")
    except Exception as e:
        print(f"  [ERROR] {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_with_correct_model())
