# 中文提示词智能翻译优化方案

## 📋 功能概述

实现中文提示词自动翻译并优化为英文的功能，提升图片生成质量。

### 核心价值
- ✅ **降低使用门槛** - 用户可以用中文输入提示词
- ✅ **提升生成质量** - 自动优化为 AI 友好的英文提示词
- ✅ **保持语义准确** - 使用 LLM 确保翻译质量
- ✅ **增强提示词** - 自动添加质量提升关键词

---

## 🏗️ 技术架构

### 1. 整体流程

```
用户输入中文提示词
    ↓
检测语言（中文/英文）
    ↓
如果是中文 → 调用 OpenAI API 翻译优化
    ↓
生成优化后的英文提示词
    ↓
调用 Grok Imagine 生成图片
```

### 2. 核心组件

```
app/services/
├── prompt_translator.py    # 提示词翻译服务（新增）
└── unified_client.py        # 统一客户端（已有）

app/api/
└── chat.py                  # Chat API（修改）
```

---

## 🔧 API 设计

### 1. 配置项（.env）

```env
# OpenAI 配置
OPENAI_API_KEY=sk-xxx                    # OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1  # OpenAI API 地址
OPENAI_MODEL=gpt-4o-mini                 # 使用的模型（推荐 gpt-4o-mini，性价比高）

# 提示词翻译功能
PROMPT_TRANSLATION_ENABLED=true          # 是否启用提示词翻译
PROMPT_ENHANCEMENT_ENABLED=true          # 是否启用提示词增强
```

### 2. API 接口

#### 方式一：自动翻译（推荐）

用户直接输入中文，系统自动检测并翻译：

```bash
curl -X POST http://localhost:9563/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "model": "grok-2-vision-1212",
    "messages": [
      {"role": "user", "content": "画一只可爱的猫咪，坐在窗台上晒太阳"}
    ],
    "stream": false
  }'
```

系统自动翻译为：
```
A cute cat sitting on a windowsill, basking in the sunlight,
warm lighting, cozy atmosphere, high detail, photorealistic
```

#### 方式二：手动翻译接口

提供独立的翻译接口，用户可以先预览翻译结果：

```bash
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "prompt": "画一只可爱的猫咪，坐在窗台上晒太阳",
    "enhance": true
  }'
```

返回：
```json
{
  "original": "画一只可爱的猫咪，坐在窗台上晒太阳",
  "translated": "A cute cat sitting on a windowsill, basking in the sunlight, warm lighting, cozy atmosphere, high detail, photorealistic",
  "language": "zh",
  "enhanced": true
}
```

---

## 📝 实现步骤

### Step 1: 创建提示词翻译服务
**文件**: `app/services/prompt_translator.py`

**功能**:
- 语言检测（中文/英文）
- 调用 OpenAI API 翻译
- 提示词优化增强
- 缓存机制（相同提示词不重复翻译）

**核心方法**:
```python
class PromptTranslator:
    async def translate(prompt: str, enhance: bool = True) -> str
    async def detect_language(text: str) -> str
    async def enhance_prompt(prompt: str) -> str
```

### Step 2: 更新配置文件
**文件**: `app/core/config.py`

**新增配置**:
- OPENAI_API_KEY
- OPENAI_BASE_URL
- OPENAI_MODEL
- PROMPT_TRANSLATION_ENABLED
- PROMPT_ENHANCEMENT_ENABLED

### Step 3: 集成到 Chat API
**文件**: `app/api/chat.py`

**修改点**:
- 在处理用户消息前，检测并翻译中文提示词
- 保留原始中文提示词（用于日志和调试）
- 使用翻译后的英文提示词调用 Grok Imagine

### Step 4: 添加独立翻译接口（可选）
**文件**: `app/api/prompts.py`（新增）

**功能**:
- 提供独立的翻译接口
- 用户可以预览翻译结果
- 支持批量翻译

### Step 5: 前端集成
**文件**: `static/index.html`, `static/app.js`

**功能**:
- 添加"翻译预览"按钮
- 显示原始中文和翻译后的英文
- 用户可以编辑翻译结果

---

## 🎯 提示词优化策略

### 1. 翻译 Prompt 模板

```
You are a professional prompt translator for AI image generation.

Task: Translate the following Chinese prompt to English and optimize it for AI image generation models like DALL-E, Midjourney, or Stable Diffusion.

Requirements:
1. Translate accurately while preserving the original meaning
2. Use descriptive, vivid language
3. Add relevant quality keywords (e.g., "high detail", "professional", "8k")
4. Add lighting and atmosphere descriptions if appropriate
5. Use comma-separated format
6. Keep it concise (under 200 words)

Chinese Prompt: {user_prompt}

Output only the optimized English prompt, without explanations.
```

### 2. 增强策略

根据提示词类型自动添加：

**人物肖像**:
- `professional photography, high detail, sharp focus`
- `portrait lighting, soft shadows`

**风景场景**:
- `landscape photography, wide angle, golden hour lighting`
- `atmospheric, cinematic composition`

**艺术风格**:
- `digital art, highly detailed, trending on artstation`
- `concept art, professional illustration`

**写实照片**:
- `photorealistic, 8k resolution, professional photography`
- `natural lighting, high dynamic range`

---

## 🔒 安全考虑

### 1. API Key 保护
- ✅ OpenAI API Key 存储在 .env 文件
- ✅ 已在 .gitignore 中配置
- ✅ 不会提交到 Git 仓库

### 2. 成本控制
- 使用 `gpt-4o-mini` 模型（成本低，速度快）
- 实现缓存机制，避免重复翻译
- 可配置每日翻译次数限制

### 3. 错误处理
- OpenAI API 调用失败时，使用原始提示词
- 记录翻译失败日志
- 提供降级方案（简单的关键词翻译）

---

## 📊 性能优化

### 1. 缓存机制
```python
# 使用内存缓存
translation_cache = {
    "prompt_hash": "translated_result"
}
```

### 2. 异步处理
- 使用 `aiohttp` 异步调用 OpenAI API
- 不阻塞主请求流程

### 3. 超时控制
- OpenAI API 调用超时时间：5秒
- 超时后使用原始提示词

---

## 🧪 测试计划

### 1. 单元测试
- 语言检测准确性
- 翻译质量
- 缓存机制
- 错误处理

### 2. 集成测试
- Chat API 端到端测试
- 翻译接口测试
- 性能测试

### 3. 测试用例

```python
# 测试用例 1: 简单描述
输入: "一只可爱的猫"
期望: "A cute cat, high detail, professional photography"

# 测试用例 2: 复杂场景
输入: "夕阳下的海滩，一对情侣牵手散步，浪漫氛围"
期望: "A couple holding hands walking on the beach at sunset, romantic atmosphere, golden hour lighting, cinematic composition, high detail"

# 测试用例 3: 艺术风格
输入: "赛博朋克风格的城市夜景，霓虹灯"
期望: "Cyberpunk style city night scene with neon lights, futuristic, sci-fi, highly detailed, digital art, vibrant colors"

# 测试用例 4: 英文输入（不翻译）
输入: "A beautiful sunset"
期望: "A beautiful sunset, high detail, professional photography"
```

---

## 📈 实施优先级

### Phase 1: 核心功能（必须）
1. ✅ 创建 PromptTranslator 服务
2. ✅ 更新配置文件
3. ✅ 集成到 Chat API
4. ✅ 基础测试

### Phase 2: 增强功能（推荐）
1. ⭐ 添加独立翻译接口
2. ⭐ 实现缓存机制
3. ⭐ 前端集成

### Phase 3: 优化功能（可选）
1. 💡 提示词模板库
2. 💡 用户自定义翻译规则
3. 💡 翻译历史记录
4. 💡 A/B 测试（对比翻译前后效果）

---

## 💰 成本估算

### OpenAI API 成本（gpt-4o-mini）

**定价**:
- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens

**单次翻译成本**:
- 平均输入：100 tokens（中文提示词 + 系统提示）
- 平均输出：50 tokens（英文提示词）
- 单次成本：约 $0.00005（0.0005元）

**月度成本估算**:
- 1000 次翻译/月：约 $0.05（0.5元）
- 10000 次翻译/月：约 $0.50（5元）
- 100000 次翻译/月：约 $5.00（50元）

**结论**: 成本极低，完全可接受

---

## 🚀 使用示例

### 示例 1: 基础使用

**输入**:
```
画一只在草地上奔跑的金毛犬
```

**自动翻译为**:
```
A golden retriever running on the grass, dynamic motion,
outdoor scene, natural lighting, high detail, professional
pet photography, joyful atmosphere
```

### 示例 2: 艺术风格

**输入**:
```
水墨画风格的山水画，远山近水，意境悠远
```

**自动翻译为**:
```
Chinese ink painting style landscape, distant mountains and
nearby water, serene and profound artistic conception,
traditional art, monochrome, elegant composition,
high artistic value
```

### 示例 3: 人物肖像

**输入**:
```
一位优雅的女性，穿着旗袍，在古典园林中
```

**自动翻译为**:
```
An elegant woman wearing a qipao (cheongsam) in a classical
Chinese garden, traditional beauty, portrait photography,
soft lighting, cultural heritage, high detail, professional
composition, refined atmosphere
```

---

## 📚 相关文档

- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [提示词工程最佳实践](https://platform.openai.com/docs/guides/prompt-engineering)
- [图片生成提示词指南](./docs/prompts.md)

---

## ✅ 验收标准

### 功能验收
- [ ] 能够准确检测中文提示词
- [ ] 翻译质量达到可用标准
- [ ] 英文提示词保持不变
- [ ] 翻译失败时有降级方案
- [ ] API 响应时间 < 3秒

### 质量验收
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 无敏感信息泄露
- [ ] 错误日志完整

### 文档验收
- [ ] API 文档更新
- [ ] 配置说明完整
- [ ] 使用示例清晰

---

## 🎉 预期效果

实施后，用户体验将显著提升：

**之前**:
- ❌ 用户需要自己翻译成英文
- ❌ 不了解提示词优化技巧
- ❌ 生成效果不稳定

**之后**:
- ✅ 直接输入中文，自动翻译
- ✅ 自动优化提示词
- ✅ 生成质量更高更稳定
- ✅ 降低使用门槛

---

**方案制定完成！准备开始实施。**
