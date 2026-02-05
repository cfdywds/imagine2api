# 🎯 智能提示词翻译 - 立即开始使用

## 📋 5 分钟快速配置

### Step 1: 配置 OpenAI API Key

编辑项目根目录的 `.env` 文件，添加以下配置：

```env
# ============ OpenAI 配置（提示词翻译）============
OPENAI_API_KEY=sk-xxx                    # 替换为你的 OpenAI API Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini                 # 推荐使用 gpt-4o-mini（性价比最高）

# ============ 提示词翻译配置 ============
PROMPT_TRANSLATION_ENABLED=true          # 启用提示词翻译
PROMPT_ENHANCEMENT_ENABLED=true          # 启用提示词增强
```

### Step 2: 重启服务

```bash
# 停止当前服务（如果正在运行）
# Ctrl+C

# 重新启动
python main.py
```

### Step 3: 测试功能

```bash
# 运行测试脚本
python test_prompt_translation.py
```

---

## 🎨 立即体验

### 测试 1: 使用 Chat API（自动翻译）

```bash
curl -X POST http://localhost:9563/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "model": "grok-2-vision-1212",
    "messages": [
      {"role": "user", "content": "画一只在草地上奔跑的金毛犬"}
    ],
    "stream": false,
    "n": 2
  }'
```

**预期效果**：
- 系统自动检测到中文
- 翻译为：`A golden retriever running on the grass, dynamic motion, outdoor scene, natural lighting, high detail, professional pet photography, joyful atmosphere`
- 生成高质量图片

### 测试 2: 使用翻译接口（预览翻译）

```bash
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "prompt": "夕阳下的海滩，一对情侣牵手散步",
    "enhance": true
  }'
```

**预期响应**：
```json
{
  "original": "夕阳下的海滩，一对情侣牵手散步",
  "translated": "A couple holding hands walking on the beach at sunset, romantic atmosphere, golden hour lighting, cinematic composition, high detail, photorealistic",
  "language": "zh",
  "enhanced": true,
  "cached": false
}
```

---

## 💡 实用示例

### 示例 1: 宠物摄影

**中文输入**：
```
一只橘猫趴在阳光下的地板上睡觉
```

**自动翻译**：
```
An orange tabby cat lying on the floor sleeping in the sunlight,
peaceful scene, warm lighting, cozy atmosphere, high detail,
professional pet photography
```

### 示例 2: 风景摄影

**中文输入**：
```
清晨的雾气笼罩着山谷，远处的山峰若隐若现
```

**自动翻译**：
```
Morning mist covering the valley, distant mountain peaks looming
in the fog, atmospheric landscape, soft diffused light, serene mood,
landscape photography, high detail, cinematic composition
```

### 示例 3: 人物肖像

**中文输入**：
```
一位年轻女性，长发飘逸，微笑着看向镜头
```

**自动翻译**：
```
A young woman with flowing long hair, smiling at the camera,
portrait photography, natural beauty, soft lighting, professional
composition, high detail, sharp focus
```

### 示例 4: 艺术创作

**中文输入**：
```
未来科幻城市，飞行汽车穿梭其间，霓虹灯闪烁
```

**自动翻译**：
```
Futuristic sci-fi city with flying cars shuttling through,
neon lights flashing, cyberpunk style, highly detailed,
digital art, vibrant colors, cinematic lighting, concept art
```

### 示例 5: 传统艺术

**中文输入**：
```
中国传统水墨画，竹林深处，一座小亭
```

**自动翻译**：
```
Traditional Chinese ink painting, deep in the bamboo forest,
a small pavilion, monochrome art, elegant composition,
artistic conception, traditional art style, high artistic value
```

---

## 🔧 高级配置

### 使用其他 OpenAI 兼容 API

如果你有其他 OpenAI 兼容的 API（如 Azure OpenAI、国内代理等），可以修改配置：

```env
# 使用 Azure OpenAI
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
OPENAI_API_KEY=your-azure-key

# 或使用国内代理
OPENAI_BASE_URL=https://api.your-proxy.com/v1
OPENAI_API_KEY=your-proxy-key
```

### 使用更强大的模型

如果需要更高质量的翻译，可以使用 GPT-4o：

```env
OPENAI_MODEL=gpt-4o
```

**注意**：GPT-4o 成本更高，约为 gpt-4o-mini 的 10 倍。

### 仅翻译不增强

如果只需要翻译，不需要自动添加质量关键词：

```env
PROMPT_ENHANCEMENT_ENABLED=false
```

---

## 📊 查看翻译效果

### 方法 1: 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# 或者查看最近的日志
tail -100 logs/app.log | grep Translator
```

**日志示例**：
```
[Translator] 检测到中文提示词，开始翻译
[Translator] 原文: 画一只可爱的猫咪
[Translator] 译文: A cute cat, high detail, professional photography
[Translator] 翻译成功
```

### 方法 2: 使用翻译接口

先预览翻译结果，满意后再生成图片：

```bash
# 1. 翻译预览
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{"prompt": "你的中文提示词", "enhance": true}'

# 2. 如果满意，使用翻译后的英文生成图片
curl -X POST http://localhost:9563/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "messages": [{"role": "user", "content": "翻译后的英文提示词"}]
  }'
```

---

## 🎯 最佳实践

### 1. 提供详细的描述

**不好的示例**：
```
一只猫
```

**好的示例**：
```
一只橘色的猫咪，坐在窗台上，阳光洒在它身上，温暖的氛围
```

**翻译效果对比**：
- 不好：`A cat, high detail, professional photography`
- 好的：`An orange cat sitting on a windowsill, sunlight shining on it, warm atmosphere, cozy scene, high detail, professional photography`

### 2. 指定风格和氛围

**示例**：
```
一座古老的城堡，哥特式建筑风格，阴沉的天气，神秘氛围
```

**翻译**：
```
An ancient castle, Gothic architectural style, gloomy weather,
mysterious atmosphere, dramatic lighting, highly detailed,
architectural photography, cinematic composition
```

### 3. 包含光照和构图信息

**示例**：
```
一位女性肖像，侧面光照，浅景深，背景虚化
```

**翻译**：
```
A woman portrait, side lighting, shallow depth of field,
blurred background, professional portrait photography,
high detail, sharp focus, bokeh effect
```

---

## 🔍 故障排查

### 问题 1: 翻译功能不工作

**症状**：输入中文后没有翻译，直接使用中文生成

**解决方案**：
1. 检查配置：
   ```bash
   cat .env | grep PROMPT_TRANSLATION_ENABLED
   cat .env | grep OPENAI_API_KEY
   ```

2. 确认配置正确：
   ```env
   PROMPT_TRANSLATION_ENABLED=true
   OPENAI_API_KEY=sk-xxx  # 不能为空
   ```

3. 重启服务：
   ```bash
   python main.py
   ```

### 问题 2: OpenAI API 调用失败

**症状**：日志显示 "OpenAI API 返回错误"

**解决方案**：
1. 检查 API Key 是否有效
2. 检查 API Key 是否有余额
3. 检查网络连接
4. 查看详细错误日志：
   ```bash
   tail -50 logs/app.log | grep -A 5 "OpenAI API"
   ```

### 问题 3: 翻译速度慢

**症状**：翻译需要 5 秒以上

**解决方案**：
1. 检查网络连接
2. 使用国内代理（如果在国内）
3. 第二次翻译会使用缓存，速度很快

### 问题 4: 翻译质量不满意

**解决方案**：
1. 使用更强大的模型：
   ```env
   OPENAI_MODEL=gpt-4o
   ```

2. 提供更详细的中文描述

3. 使用翻译接口预览，手动调整后使用

---

## 📈 监控和管理

### 查看缓存统计

```bash
curl http://localhost:9563/v1/prompts/cache-stats \
  -H "Authorization: Bearer admin"
```

**响应示例**：
```json
{
  "cache_size": 25,
  "cache_entries": ["hash1", "hash2", "..."]
}
```

### 清空缓存

当缓存过大或需要重新翻译时：

```bash
curl -X POST http://localhost:9563/v1/prompts/clear-cache \
  -H "Authorization: Bearer admin"
```

### 监控成本

查看 OpenAI 使用情况：
1. 访问 https://platform.openai.com/usage
2. 查看 API 调用次数和成本
3. 设置使用限额（推荐）

---

## 🎉 开始使用

现在你已经完成了所有配置，可以开始使用智能提示词翻译功能了！

### 快速测试命令

```bash
# 测试 1: 简单描述
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{"prompt": "一只可爱的猫", "enhance": true}'

# 测试 2: 复杂场景
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{"prompt": "夕阳下的海滩，浪漫氛围", "enhance": true}'

# 测试 3: 生成图片
curl -X POST http://localhost:9563/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "messages": [{"role": "user", "content": "画一只在草地上奔跑的金毛犬"}],
    "n": 2
  }'
```

---

## 📚 更多资源

- **详细设计方案**: [PROMPT_TRANSLATION_PLAN.md](./PROMPT_TRANSLATION_PLAN.md)
- **使用指南**: [PROMPT_TRANSLATION_GUIDE.md](./PROMPT_TRANSLATION_GUIDE.md)
- **实施报告**: [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md)
- **API 文档**: http://localhost:9563/docs
- **主文档**: [README.md](./README.md)

---

## 💬 获取帮助

遇到问题？
1. 查看日志：`tail -f logs/app.log`
2. 运行测试：`python test_prompt_translation.py`
3. 查看文档：上述资源链接
4. 提交 Issue：https://github.com/cfdywds/imagine2api/issues

---

**祝你使用愉快！** 🎨✨

现在就开始用中文创作精美的 AI 图片吧！
