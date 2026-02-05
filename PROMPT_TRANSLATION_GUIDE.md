# 🌐 智能提示词翻译 - 快速使用指南

## 📋 功能简介

将中文提示词自动翻译并优化为英文，提升图片生成质量。

**核心价值**：
- ✅ 用户直接输入中文，无需手动翻译
- ✅ 自动优化为 AI 友好的英文提示词
- ✅ 提升生成质量和稳定性
- ✅ 成本极低（每次约 0.0005 元）

---

## 🚀 快速开始

### 1. 配置 OpenAI API Key

编辑 `.env` 文件，添加以下配置：

```env
# OpenAI 配置（用于提示词翻译）
OPENAI_API_KEY=sk-xxx                    # 你的 OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini                 # 推荐使用 gpt-4o-mini

# 启用提示词翻译
PROMPT_TRANSLATION_ENABLED=true
PROMPT_ENHANCEMENT_ENABLED=true
```

### 2. 重启服务

```bash
python main.py
```

### 3. 测试功能

```bash
# 测试翻译功能
python test_prompt_translation.py
```

---

## 💡 使用方式

### 方式 1: 自动翻译（推荐）

直接在 Chat API 中输入中文，系统自动翻译：

```bash
curl -X POST http://localhost:9563/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "model": "grok-2-vision-1212",
    "messages": [
      {"role": "user", "content": "画一只可爱的猫咪，坐在窗台上晒太阳"}
    ],
    "stream": false,
    "n": 2
  }'
```

**翻译效果**：
- 输入：`画一只可爱的猫咪，坐在窗台上晒太阳`
- 翻译：`A cute cat sitting on a windowsill, basking in the sunlight, warm lighting, cozy atmosphere, high detail, photorealistic`

### 方式 2: 独立翻译接口

先预览翻译结果，再决定是否使用：

```bash
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "prompt": "画一只可爱的猫咪，坐在窗台上晒太阳",
    "enhance": true
  }'
```

**响应示例**：
```json
{
  "original": "画一只可爱的猫咪，坐在窗台上晒太阳",
  "translated": "A cute cat sitting on a windowsill, basking in the sunlight, warm lighting, cozy atmosphere, high detail, photorealistic",
  "language": "zh",
  "enhanced": true,
  "cached": false
}
```

---

## 🎨 翻译示例

### 示例 1: 简单描述

**输入**：
```
一只可爱的猫
```

**翻译**：
```
A cute cat, high detail, professional photography
```

### 示例 2: 复杂场景

**输入**：
```
夕阳下的海滩，一对情侣牵手散步，浪漫氛围
```

**翻译**：
```
A couple holding hands walking on the beach at sunset, romantic atmosphere,
golden hour lighting, cinematic composition, high detail, photorealistic
```

### 示例 3: 艺术风格

**输入**：
```
赛博朋克风格的城市夜景，霓虹灯闪烁
```

**翻译**：
```
Cyberpunk style city night scene with neon lights, futuristic, sci-fi,
highly detailed, digital art, vibrant colors, atmospheric lighting
```

### 示例 4: 人物肖像

**输入**：
```
一位优雅的女性，穿着旗袍，在古典园林中
```

**翻译**：
```
An elegant woman wearing a qipao (cheongsam) in a classical Chinese garden,
traditional beauty, portrait photography, soft lighting, cultural heritage,
high detail, professional composition, refined atmosphere
```

### 示例 5: 水墨画风格

**输入**：
```
水墨画风格的山水画，远山近水，意境悠远
```

**翻译**：
```
Chinese ink painting style landscape, distant mountains and nearby water,
serene and profound artistic conception, traditional art, monochrome,
elegant composition, high artistic value
```

---

## 🔧 管理功能

### 查看缓存统计

```bash
curl http://localhost:9563/v1/prompts/cache-stats \
  -H "Authorization: Bearer admin"
```

**响应**：
```json
{
  "cache_size": 15,
  "cache_entries": ["hash1", "hash2", "..."]
}
```

### 清空翻译缓存

```bash
curl -X POST http://localhost:9563/v1/prompts/clear-cache \
  -H "Authorization: Bearer admin"
```

**响应**：
```json
{
  "success": true,
  "message": "Cache cleared, 15 entries removed"
}
```

---

## ⚙️ 配置说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-xxx` |
| `PROMPT_TRANSLATION_ENABLED` | 是否启用翻译 | `true` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_BASE_URL` | API 地址 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 使用的模型 | `gpt-4o-mini` |
| `PROMPT_ENHANCEMENT_ENABLED` | 是否增强英文提示词 | `true` |

### 推荐配置

```env
# 使用 gpt-4o-mini（性价比最高）
OPENAI_MODEL=gpt-4o-mini

# 启用翻译和增强
PROMPT_TRANSLATION_ENABLED=true
PROMPT_ENHANCEMENT_ENABLED=true
```

---

## 💰 成本说明

### gpt-4o-mini 定价

- **Input**: $0.150 / 1M tokens
- **Output**: $0.600 / 1M tokens

### 单次翻译成本

- 平均输入：100 tokens（中文提示词 + 系统提示）
- 平均输出：50 tokens（英文提示词）
- **单次成本**：约 **$0.00005**（**0.0005 元**）

### 月度成本估算

| 翻译次数/月 | 月度成本（美元） | 月度成本（人民币） |
|------------|-----------------|-------------------|
| 1,000 次 | $0.05 | ¥0.5 |
| 10,000 次 | $0.50 | ¥5 |
| 100,000 次 | $5.00 | ¥50 |

**结论**：成本极低，完全可接受 ✅

---

## 🎯 优化策略

### 自动添加的质量关键词

根据提示词类型，系统会自动添加相应的质量关键词：

**人物肖像**：
- `professional photography, high detail, sharp focus`
- `portrait lighting, soft shadows`

**风景场景**：
- `landscape photography, wide angle, golden hour lighting`
- `atmospheric, cinematic composition`

**艺术风格**：
- `digital art, highly detailed, trending on artstation`
- `concept art, professional illustration`

**写实照片**：
- `photorealistic, 8k resolution, professional photography`
- `natural lighting, high dynamic range`

---

## 🔍 工作原理

### 翻译流程

```
用户输入中文提示词
    ↓
检测语言（中文/英文）
    ↓
如果是中文 → 调用 OpenAI API
    ↓
翻译 + 优化 + 添加质量关键词
    ↓
返回优化后的英文提示词
    ↓
调用 Grok Imagine 生成图片
```

### 缓存机制

- 使用 MD5 哈希作为缓存键
- 相同的提示词不会重复翻译
- 节省成本和时间
- 可手动清空缓存

### 错误处理

- OpenAI API 调用失败 → 使用原始提示词
- 超时（5秒）→ 使用原始提示词
- 记录详细日志，便于调试

---

## 🧪 测试

### 运行测试脚本

```bash
python test_prompt_translation.py
```

### 测试内容

1. ✅ 语言检测准确性
2. ✅ 翻译质量
3. ✅ 缓存机制
4. ✅ API 集成
5. ✅ 错误处理

---

## ❓ 常见问题

### Q1: 翻译功能不工作？

**检查清单**：
1. 确认 `OPENAI_API_KEY` 已配置
2. 确认 `PROMPT_TRANSLATION_ENABLED=true`
3. 检查 OpenAI API Key 是否有效
4. 查看日志：`tail -f logs/app.log`

### Q2: 如何使用自己的 OpenAI 兼容 API？

修改 `OPENAI_BASE_URL`：
```env
OPENAI_BASE_URL=https://your-api.com/v1
```

### Q3: 英文提示词会被翻译吗？

不会。系统会自动检测语言，英文提示词保持不变（可选增强）。

### Q4: 如何禁用翻译功能？

设置 `PROMPT_TRANSLATION_ENABLED=false` 或删除该配置项。

### Q5: 翻译结果不满意怎么办？

1. 使用独立翻译接口预览结果
2. 调整 `OPENAI_MODEL`（如使用 `gpt-4o`）
3. 手动编辑翻译结果后使用

---

## 📊 性能优化

### 缓存策略

- 内存缓存，快速响应
- 相同提示词命中缓存，0 成本
- 建议定期清空缓存（避免内存占用）

### 超时控制

- OpenAI API 调用超时：5 秒
- 超时后自动降级，使用原始提示词
- 不影响用户体验

### 异步处理

- 使用 `aiohttp` 异步调用
- 不阻塞主请求流程
- 提升整体性能

---

## 🎉 效果对比

### 使用翻译前

**用户输入**：
```
画一只猫
```

**生成效果**：
- ❌ 可能理解不准确
- ❌ 质量不稳定
- ❌ 缺少细节

### 使用翻译后

**用户输入**：
```
画一只猫
```

**自动翻译为**：
```
A cat, high detail, professional photography
```

**生成效果**：
- ✅ 理解准确
- ✅ 质量稳定
- ✅ 细节丰富

---

## 📚 相关文档

- [完整设计方案](./PROMPT_TRANSLATION_PLAN.md)
- [API 文档](http://localhost:9563/docs)
- [主文档](./README.md)

---

## 🆘 获取帮助

如有问题或建议：
1. 查看日志：`tail -f logs/app.log`
2. 运行测试：`python test_prompt_translation.py`
3. 提交 Issue：https://github.com/cfdywds/imagine2api/issues

---

**祝使用愉快！** 🎨✨
