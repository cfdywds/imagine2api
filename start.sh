#!/bin/bash
# Imagine2API - 一键启动脚本

echo "=================================="
echo "  Imagine2API - 启动脚本"
echo "=================================="
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python"
    echo "请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python 版本: $(python --version)"

# 检查依赖
echo ""
echo "检查依赖..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  缺少依赖，正在安装..."
    pip install -r requirements.txt
else
    echo "✓ 依赖已安装"
fi

# 检查 key.txt
echo ""
if [ ! -f "key.txt" ]; then
    echo "⚠️  警告: key.txt 文件不存在"
    echo "请创建 key.txt 文件并添加 Grok SSO Token"
    echo ""
    read -p "是否继续启动? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ key.txt 文件存在"
fi

# 检查 .env
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，将自动创建"
fi

# 启动服务
echo ""
echo "=================================="
echo "  启动服务..."
echo "=================================="
echo ""
echo "服务地址: http://localhost:9563"
echo "API 文档: http://localhost:9563/docs"
echo "健康检查: http://localhost:9563/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python main.py
