#!/bin/bash
# Formspree 配置脚本
# 使用方法: bash configure_formspree.sh YOUR_FORM_ID

if [ -z "$1" ]; then
  echo "❌ 错误：请提供 Formspree Form ID"
  echo ""
  echo "使用方法："
  echo "  bash configure_formspree.sh YOUR_FORM_ID"
  echo ""
  echo "示例："
  echo "  bash configure_formspree.sh xyzabc123"
  echo ""
  echo "📖 如何获取 Form ID："
  echo "  1. 访问 https://formspree.io/ 并注册"
  echo "  2. 创建新表单"
  echo "  3. 复制 Form ID（格式如：xyzabc123）"
  echo ""
  exit 1
fi

FORM_ID=$1

echo "🔧 正在配置 Formspree..."
echo "Form ID: $FORM_ID"
echo ""

# 替换 rebuild_site_v2.py 中的 Form ID
sed -i '' "s/YOUR_FORM_ID/$FORM_ID/g" rebuild_site_v2.py

if [ $? -eq 0 ]; then
  echo "✅ rebuild_site_v2.py 已更新"
else
  echo "❌ 更新失败"
  exit 1
fi

# 重新生成网站
echo ""
echo "🔨 重新生成网站..."
python3 rebuild_site_v2.py

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 网站生成成功！"
  echo ""
  echo "📁 生成的文件："
  echo "  - index.html"
  echo "  - search.html"
  echo "  - categories/ (10 个分类页)"
  echo "  - products/ (161 个产品页)"
  echo ""
  echo "🚀 下一步："
  echo "  运行 bash deploy.sh 部署到 GitHub Pages"
  echo ""
else
  echo "❌ 网站生成失败"
  exit 1
fi
