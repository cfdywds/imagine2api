"""提示词翻译功能测试"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from app.services.prompt_translator import PromptTranslator


async def test_language_detection():
    """测试语言检测"""
    print("\n=== 测试语言检测 ===")

    translator = PromptTranslator()

    test_cases = [
        ("一只可爱的猫", "zh"),
        ("A cute cat", "en"),
        ("画一幅山水画", "zh"),
        ("Beautiful sunset over the ocean", "en"),
        ("赛博朋克风格的城市", "zh"),
    ]

    for text, expected in test_cases:
        detected = translator.detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"{status} '{text}' -> {detected} (期望: {expected})")


async def test_translation():
    """测试翻译功能"""
    print("\n=== 测试翻译功能 ===")

    translator = PromptTranslator()

    test_cases = [
        "一只可爱的猫咪，坐在窗台上晒太阳",
        "夕阳下的海滩，一对情侣牵手散步，浪漫氛围",
        "赛博朋克风格的城市夜景，霓虹灯闪烁",
        "水墨画风格的山水画，远山近水，意境悠远",
        "一位优雅的女性，穿着旗袍，在古典园林中",
    ]

    for i, prompt in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"原文: {prompt}")

        try:
            translated = await translator.translate(prompt, enhance=True)
            print(f"译文: {translated}")
            print("状态: ✓ 成功")
        except Exception as e:
            print(f"状态: ✗ 失败 - {e}")


async def test_english_enhancement():
    """测试英文提示词增强"""
    print("\n=== 测试英文提示词增强 ===")

    translator = PromptTranslator()

    test_cases = [
        "A cute cat",
        "Beautiful sunset",
        "Cyberpunk city at night",
    ]

    for prompt in test_cases:
        print(f"\n原文: {prompt}")

        try:
            enhanced = await translator.translate(prompt, enhance=True)
            print(f"增强: {enhanced}")
            print("状态: ✓ 成功")
        except Exception as e:
            print(f"状态: ✗ 失败 - {e}")


async def test_cache():
    """测试缓存机制"""
    print("\n=== 测试缓存机制 ===")

    translator = PromptTranslator()

    prompt = "一只可爱的猫咪"

    print(f"第一次翻译: {prompt}")
    try:
        result1 = await translator.translate(prompt)
        print(f"结果: {result1}")
        print(f"缓存大小: {len(translator.cache)}")
    except Exception as e:
        print(f"失败: {e}")
        return

    print(f"\n第二次翻译（应该使用缓存）: {prompt}")
    try:
        result2 = await translator.translate(prompt)
        print(f"结果: {result2}")
        print(f"缓存大小: {len(translator.cache)}")

        if result1 == result2:
            print("状态: ✓ 缓存工作正常")
        else:
            print("状态: ✗ 缓存结果不一致")
    except Exception as e:
        print(f"失败: {e}")


async def test_api_integration():
    """测试 API 集成"""
    print("\n=== 测试 API 集成 ===")

    import aiohttp

    base_url = "http://localhost:9563"
    api_key = "admin"

    # 测试翻译接口
    print("\n1. 测试翻译接口")
    url = f"{base_url}/v1/prompts/translate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": "画一只可爱的猫咪",
        "enhance": True
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"原文: {result['original']}")
                    print(f"译文: {result['translated']}")
                    print(f"语言: {result['language']}")
                    print(f"增强: {result['enhanced']}")
                    print(f"缓存: {result['cached']}")
                    print("状态: ✓ 成功")
                else:
                    error = await response.text()
                    print(f"状态: ✗ 失败 ({response.status}) - {error}")
    except Exception as e:
        print(f"状态: ✗ 连接失败 - {e}")
        print("提示: 请确保服务已启动 (python main.py)")

    # 测试缓存统计
    print("\n2. 测试缓存统计接口")
    url = f"{base_url}/v1/prompts/cache-stats"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"缓存大小: {result['cache_size']}")
                    print("状态: ✓ 成功")
                else:
                    error = await response.text()
                    print(f"状态: ✗ 失败 ({response.status}) - {error}")
    except Exception as e:
        print(f"状态: ✗ 连接失败 - {e}")


async def main():
    """主测试函数"""
    print("=" * 60)
    print("提示词翻译功能测试")
    print("=" * 60)

    # 检查配置
    from app.core.config import settings

    print("\n配置检查:")
    print(f"PROMPT_TRANSLATION_ENABLED: {getattr(settings, 'PROMPT_TRANSLATION_ENABLED', False)}")
    print(f"OPENAI_API_KEY: {'已配置' if getattr(settings, 'OPENAI_API_KEY', '') else '未配置'}")
    print(f"OPENAI_MODEL: {getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')}")

    if not getattr(settings, 'OPENAI_API_KEY', ''):
        print("\n⚠️  警告: OPENAI_API_KEY 未配置，翻译功能将无法使用")
        print("请在 .env 文件中配置 OPENAI_API_KEY")
        return

    # 运行测试
    await test_language_detection()

    if getattr(settings, 'PROMPT_TRANSLATION_ENABLED', False):
        await test_translation()
        await test_english_enhancement()
        await test_cache()
        await test_api_integration()
    else:
        print("\n⚠️  提示词翻译功能未启用")
        print("请在 .env 文件中设置 PROMPT_TRANSLATION_ENABLED=true")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
