"""测试 API 端点的中转站模式"""

import requests
import json

BASE_URL = "http://localhost:9563/v1"
API_KEY = "admin"

def test_chat_completions():
    """测试 Chat Completions 端点"""
    print("=" * 60)
    print("测试 Chat Completions API")
    print("=" * 60)

    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-4-fast",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "stream": False
    }

    print("\n[1] 发送请求...")
    print(f"  URL: {url}")
    print(f"  Model: {payload['model']}")
    print(f"  Message: {payload['messages'][0]['content']}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"\n[2] 响应状态: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n[3] 响应内容:")
            print(f"  ID: {data.get('id', 'N/A')}")
            print(f"  Model: {data.get('model', 'N/A')}")

            choices = data.get('choices', [])
            if choices:
                message = choices[0].get('message', {})
                content = message.get('content', '')
                print(f"  Content: {content[:100]}...")

            print("\n[OK] Chat Completions 测试成功!")
            return True
        else:
            print(f"\n[FAIL] 请求失败: {response.status_code}")
            print(f"  错误: {response.text}")
            return False

    except Exception as e:
        print(f"\n[ERROR] 请求异常: {e}")
        return False


def test_imagine_api():
    """测试图片生成 API"""
    print("\n" + "=" * 60)
    print("测试 Image Generation API")
    print("=" * 60)

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": "a beautiful sunset over the ocean",
        "model": "grok-imagine",
        "n": 2,
        "size": "1024x1536",
        "response_format": "url",
        "stream": False
    }

    print("\n[1] 发送请求...")
    print(f"  URL: {url}")
    print(f"  Prompt: {payload['prompt']}")
    print(f"  N: {payload['n']}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print(f"\n[2] 响应状态: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n[3] 响应内容:")
            print(f"  Created: {data.get('created', 'N/A')}")

            images = data.get('data', [])
            print(f"  Images: {len(images)}")

            for i, img in enumerate(images, 1):
                url = img.get('url', 'N/A')
                print(f"    [{i}] {url[:80]}...")

            print("\n[OK] Image Generation 测试成功!")
            return True
        else:
            print(f"\n[FAIL] 请求失败: {response.status_code}")
            print(f"  错误: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"\n[ERROR] 请求异常: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("API Endpoint Test - Relay Mode")
    print("=" * 60)
    print("\nNote: Service should be running (python main.py)")
    print("Note: RELAY_ENABLED=true in .env")
    print("\nStarting tests...\n")

    # 测试 Chat
    chat_ok = test_chat_completions()

    # 测试图片生成
    image_ok = test_imagine_api()

    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Chat Completions: {'PASS' if chat_ok else 'FAIL'}")
    print(f"  Image Generation: {'PASS' if image_ok else 'FAIL'}")
    print("=" * 60)
