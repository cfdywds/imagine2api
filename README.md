# Grok Imagine API Gateway

Grok 图片生成 API 代理网关，将 Grok Imagine 封装为 OpenAI 兼容的 REST API。

支持两种模式：**中转站模式**（推荐）和 **直连模式**，灵活切换，简单易用。

## ✨ 功能特性

### 核心功能

- **🔄 双模式支持** - 中转站模式（HTTP API）+ 直连模式（WebSocket）
- **🎨 OpenAI 兼容 API** - 完全兼容 OpenAI 的 API 格式
- **🖼️ 图片生成** - 文本生成图片 + 图生图（4 种模式）
- **💬 Chat Completions** - 支持流式和非流式响应
- **🌐 智能提示词翻译** ⭐ - 中文自动翻译优化为英文（新功能）
- **🔑 API Key 管理** - 多用户支持，独立配置和限制
- **📊 使用统计** - 详细的使用记录和监控

### 高级特性

- **多 SSO 管理** - 支持多账号轮询，内置多种轮询策略
- **图片缓存** - 自动保存生成的图片
- **Redis 支持** - 可选的分布式会话持久化
- **代理支持** - 支持 HTTP/HTTPS/SOCKS5 代理
- **性能优化** - 连接池、DNS 缓存、自动重试

## 🚀 快速开始

### 方式 1: 中转站模式（推荐）⭐

**优点**: 无需 SSO Token，配置简单，更稳定

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

创建或编辑 `.env` 文件：

```env
# 启用中转站模式
RELAY_ENABLED=true
RELAY_BASE_URL=https://api.yexc.top/v1
RELAY_API_KEY=your-relay-api-key

# 提示词翻译（可选）
PROMPT_TRANSLATION_ENABLED=true
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini

# 服务器配置
HOST=0.0.0.0
PORT=9563
API_KEY=admin
```

#### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:9563` 启动。

---

### 方式 2: 直连模式

**适用场景**: 需要使用特定 Grok 功能，或中转站不可用时

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置 SSO

在项目根目录创建 `key.txt` 文件，每行一个 SSO Token：

```
your-sso-token-1
your-sso-token-2
```

#### 3. 配置环境变量

```env
# 禁用中转站模式
RELAY_ENABLED=false

# SSO 配置
SSO_FILE=key.txt
SSO_ROTATION_STRATEGY=hybrid
SSO_DAILY_LIMIT=10

# 服务器配置
HOST=0.0.0.0
PORT=9563
API_KEY=admin
```

#### 4. 启动服务

```bash
python main.py
```

## 📚 API 接口

### Chat Completions

支持中文提示词，自动翻译为英文（需配置 OpenAI API Key）：

```bash
curl -X POST http://localhost:9563/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "model": "grok-4-fast",
    "messages": [{"role": "user", "content": "画一只可爱的猫咪，坐在窗台上晒太阳"}],
    "stream": false
  }'
```

**提示词翻译示例**：
- 输入：`画一只可爱的猫咪，坐在窗台上晒太阳`
- 自动翻译为：`A cute cat sitting on a windowsill, basking in the sunlight, warm lighting, cozy atmosphere, high detail, photorealistic`

### 图片生成

```bash
curl -X POST http://localhost:9563/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "prompt": "a beautiful sunset over mountains",
    "n": 2,
    "size": "1024x1536"
  }'
```

### 图生图（新功能）

```bash
curl -X POST http://localhost:9563/v1/images/edit \
  -H "Authorization: Bearer admin" \
  -F "prompt=make it look like a painting" \
  -F "image=@test_image.jpg" \
  -F "mode=style_transfer" \
  -F "strength=0.8"
```

**支持的模式**:
- `style_transfer` - 风格迁移
- `upscale` - 图片放大
- `inpainting` - 图片修复
- `background_replace` - 背景替换

### API Key 管理

```bash
# 创建 API Key
curl -X POST http://localhost:9563/admin/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API",
    "daily_limit": 100,
    "monthly_limit": 3000
  }'

# 列出所有 API Keys
curl http://localhost:9563/admin/api-keys

# 获取使用统计
curl http://localhost:9563/admin/api-keys-stats
```

## 🗺️ 路由说明

### 用户 API

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/api` | GET | API 服务信息 |
| `/docs` | GET | Swagger API 文档 |
| `/health` | GET | 健康检查 |
| `/v1/chat/completions` | POST | Chat Completions API |
| `/v1/images/generations` | POST | 文本生成图片 |
| `/v1/images/edit` | POST | 图生图 |
| `/v1/prompts/translate` | POST | 翻译提示词 ⭐ |
| `/v1/prompts/cache-stats` | GET | 缓存统计 |
| `/v1/prompts/clear-cache` | POST | 清空缓存 |
| `/v1/models` | GET | 列出可用模型 |
| `/images/{filename}` | GET | 访问生成的图片 |

### 提示词翻译 API（新功能）⭐

```bash
# 翻译提示词
curl -X POST http://localhost:9563/v1/prompts/translate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "prompt": "画一只可爱的猫咪",
    "enhance": true
  }'

# 响应示例
{
  "original": "画一只可爱的猫咪",
  "translated": "A cute cat, high detail, professional photography",
  "language": "zh",
  "enhanced": true,
  "cached": false
}

# 获取缓存统计
curl http://localhost:9563/v1/prompts/cache-stats \
  -H "Authorization: Bearer admin"

# 清空翻译缓存
curl -X POST http://localhost:9563/v1/prompts/clear-cache \
  -H "Authorization: Bearer admin"
```

### 管理 API

| 路径 | 方法 | 说明 |
|------|------|------|
| `/admin/status` | GET | 服务状态 |
| `/admin/sso/list` | GET | SSO Token 列表 |
| `/admin/sso/add` | POST | 添加 SSO Token |
| `/admin/sso/remove` | POST | 移除 SSO Token |
| `/admin/images/clear` | POST | 清空图片缓存 |
| `/admin/api-keys` | POST | 创建 API Key |
| `/admin/api-keys` | GET | 列出 API Keys |
| `/admin/api-keys/{key}` | GET | 获取 Key 详情 |
| `/admin/api-keys/{key}` | PUT | 更新 Key 配置 |
| `/admin/api-keys/{key}` | DELETE | 删除 API Key |
| `/admin/api-keys-stats` | GET | 使用统计 |

## 📁 项目结构

```
├── app/
│   ├── api/
│   │   ├── admin.py          # 管理接口（SSO、API Key）
│   │   ├── chat.py           # Chat Completions API
│   │   └── imagine.py        # 图片生成 API
│   ├── core/
│   │   ├── config.py         # 配置管理
│   │   └── logger.py         # 日志系统
│   ├── middleware/
│   │   └── auth.py           # 认证中间件
│   ├── models/
│   │   └── api_key.py        # API Key 数据模型
│   └── services/
│       ├── grok_client.py    # Grok WebSocket 客户端
│       ├── relay_client.py   # 中转站 HTTP 客户端
│       ├── unified_client.py # 统一客户端（自动模式切换）
│       ├── api_key_manager.py # API Key 管理器
│       ├── sso_manager.py    # SSO 管理（本地）
│       └── redis_sso_manager.py # SSO 管理（Redis）
├── data/
│   └── images/               # 图片缓存目录
├── static/                   # 静态文件（前端）
├── main.py                   # 入口文件
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量配置
└── key.txt                   # SSO Token 文件（直连模式）
```

## ⚙️ 配置项说明

### 中转站模式配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RELAY_ENABLED` | `false` | 启用中转站模式 |
| `RELAY_BASE_URL` | - | 中转站 API 地址 |
| `RELAY_API_KEY` | - | 中转站 API Key |
| `RELAY_CHAT_MODEL` | `grok-4-fast` | Chat 模型 |
| `RELAY_IMAGE_MODEL` | `grok-imagine-0.9` | 图片模型 |

### 服务器配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `9563` | 服务端口 |
| `DEBUG` | `false` | 调试模式 |
| `API_KEY` | `admin` | 默认 API Key |

### 直连模式配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `SSO_FILE` | `key.txt` | SSO Token 文件路径 |
| `SSO_ROTATION_STRATEGY` | `hybrid` | 轮询策略 |
| `SSO_DAILY_LIMIT` | `10` | 每 Key 日限制 |
| `PROXY_URL` | - | 代理地址 |
| `GENERATION_TIMEOUT` | `180` | 生成超时(秒) |

### Redis 配置（可选）

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `REDIS_ENABLED` | `false` | 启用 Redis |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 地址 |

### 其他配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `BASE_URL` | - | 外部访问地址 |
| `DEFAULT_ASPECT_RATIO` | `2:3` | 默认宽高比 |

## 📖 文档

完整文档请查看 [docs/](./docs/) 目录。

### 核心文档

- **[快速开始指南](./docs/quick-start.md)** ⭐ - 3 步快速启动
- **[中转站模式指南](./docs/relay-guide.md)** - 详细使用指南
- **[图生图指南](./docs/image-to-image.md)** - 4 种图生图模式
- **[提示词模板](./docs/prompts.md)** ⭐ - 提示词最佳实践

### 文档索引

查看 [docs/README.md](./docs/README.md) 获取完整的文档目录和导航。

## 🧪 测试

### 运行测试

```bash
# API 端点测试（推荐）
python test_api_relay.py

# 集成测试
python test_integration.py

# 中转站测试
python test_relay.py
python test_relay_models.py
python test_relay_correct.py
```

### 预期输出

```
============================================================
Test Summary
============================================================
  Chat Completions: PASS
  Image Generation: PASS
============================================================
```

## 🔄 模式切换

### 切换到中转站模式

编辑 `.env` 文件：

```env
RELAY_ENABLED=true
RELAY_BASE_URL=https://api.yexc.top/v1
RELAY_API_KEY=your-api-key
```

重启服务后生效。

### 切换到直连模式

编辑 `.env` 文件：

```env
RELAY_ENABLED=false
SSO_FILE=key.txt
```

确保 `key.txt` 文件包含有效的 SSO Token，然后重启服务。

## 🎯 使用场景

### 中转站模式适用于

- ✅ 不想管理 SSO Token
- ✅ 需要稳定的 HTTP API
- ✅ 快速部署和使用
- ✅ 标准 OpenAI 格式集成

### 直连模式适用于

- ✅ 需要完全控制
- ✅ 有可用的 SSO Token
- ✅ 需要特定 Grok 功能
- ✅ 中转站服务不可用时

## 🚨 注意事项

### 安全

- ⚠️ 妥善保管 API Key 和 SSO Token
- ⚠️ 不要将密钥提交到 Git
- ⚠️ 定期轮换密钥
- ⚠️ 使用环境变量管理敏感信息

### 存储

- ⚠️ 定期清理 `data/images/` 目录
- ⚠️ 监控磁盘空间使用
- ⚠️ 考虑使用对象存储（如 S3）

### 性能

- ⚠️ 根据负载调整连接池大小
- ⚠️ 监控 API 响应时间
- ⚠️ 设置合理的超时时间

## 📊 性能指标

### 响应时间

- **Chat Completions**: ~6 秒
- **Image Generation**: ~10 秒（2 张图片）
- **Image-to-Image**: ~8 秒

### 并发支持

- 连接池大小：100
- 每主机连接：30
- DNS 缓存：300 秒
- WebSocket 超时：90 秒

## 🛠️ 故障排查

### 服务无法启动

```bash
# 检查端口占用
netstat -ano | findstr :9563

# 检查配置
cat .env

# 查看日志
tail -f logs/app.log
```

### API 返回 401

- 检查 Authorization header 格式
- 验证 API Key 是否正确
- 确认 API Key 未过期或被禁用

### 中转站连接失败

```bash
# 测试中转站连接
curl https://api.yexc.top/v1/models \
  -H "Authorization: Bearer your-api-key"

# 检查网络连接
ping api.yexc.top
```

### 图片生成失败

- 检查 SSO Token 是否有效（直连模式）
- 确认中转站 API Key 有效（中转站模式）
- 查看日志获取详细错误信息
- 检查是否达到请求限制

## 🔗 相关链接

- **API 文档**: http://localhost:9563/docs
- **服务状态**: http://localhost:9563/admin/status
- **GitHub**: [项目地址]

## 📝 更新日志

### v2.1.0 (2026-02-04)

- ✅ 新增中转站模式支持
- ✅ 新增 API Key 管理系统
- ✅ 新增图生图功能
- ✅ 优化连接处理和性能
- ✅ 完善文档和测试

### v2.0.0

- ✅ OpenAI 兼容 API
- ✅ WebSocket 直连支持
- ✅ 多 SSO 管理
- ✅ Redis 支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT

---

**🎉 现在就开始使用 Grok Imagine API Gateway！**

查看 [快速开始_中转站模式.md](./快速开始_中转站模式.md) 获取详细指南。
