"""测试中转站支持的模型"""

import asyncio
import aiohttp


async def test_relay_models():
    """测试中转站支持的模型"""
    base_url = "https://api.yexc.top/v1"
    api_key = "sk-KxqASAFTrc4mkE1425v8W2mPZpWrSrPQqjhZm7cjpPA7yR0Q"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("=" * 60)
    print("测试中转站支持的模型")
    print("=" * 60)

    # 1. 测试获取模型列表
    print("\n[1] 获取模型列表...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/models", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"[OK] 获取成功")
                    models = data.get("data", [])
                    print(f"  共 {len(models)} 个模型:")
                    for model in models[:10]:  # 只显示前10个
                        print(f"    - {model.get('id')}")
                else:
                    text = await response.text()
                    print(f"[FAIL] 获取失败: {response.status}")
                    print(f"  响应: {text}")
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")

    # 2. 测试图片生成（尝试不同的模型）
    print("\n[2] 测试图片生成...")
    test_models = ["dall-e-3", "dall-e-2", "grok-imagine", "flux", "stable-diffusion"]

    for model in test_models:
        print(f"\n  测试模型: {model}")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": "a cute cat",
                    "n": 1
                }
                async with session.post(
                    f"{base_url}/images/generations",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"    [OK] 成功！")
                        break
                    else:
                        text = await response.text()
                        print(f"    [FAIL] {response.status}")
        except Exception as e:
            print(f"    [ERROR] {e}")

    # 3. 测试 Chat（尝试不同的模型）
    print("\n[3] 测试 Chat Completions...")
    test_chat_models = ["gpt-4", "gpt-3.5-turbo", "grok", "claude-3"]

    for model in test_chat_models:
        print(f"\n  测试模型: {model}")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "stream": False
                }
                async with session.post(
                    f"{base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"    [OK] 成功！")
                        break
                    else:
                        text = await response.text()
                        print(f"    [FAIL] {response.status}")
        except Exception as e:
            print(f"    [ERROR] {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_relay_models())
