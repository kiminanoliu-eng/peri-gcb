#!/bin/bash
# Web3Forms 配置脚本
# 使用方法: bash configure_web3forms.sh YOUR_ACCESS_KEY

if [ -z "$1" ]; then
  echo "❌ 错误：请提供 Web3Forms Access Key"
  echo ""
  echo "使用方法："
  echo "  bash configure_web3forms.sh YOUR_ACCESS_KEY"
  echo ""
  echo "示例："
  echo "  bash configure_web3forms.sh abc123def456"
  echo ""
  echo "📖 如何获取 Access Key："
  echo "  1. 访问 https://web3forms.com"
  echo "  2. 点击 'Get Started Free'"
  echo "  3. 输入你的邮箱地址"
  echo "  4. 点击 'Create Access Key'"
  echo "  5. 复制 Access Key（格式如：abc123def456）"
  echo ""
  echo "✨ Web3Forms 优势："
  echo "  - 完全免费，无限制"
  echo "  - 无需注册账号"
  echo "  - 自动垃圾邮件过滤"
  echo "  - 支持文件上传"
  echo ""
  exit 1
fi

ACCESS_KEY=$1

echo "🔧 正在配置 Web3Forms..."
echo "Access Key: $ACCESS_KEY"
echo ""

# 替换 rebuild_site_v2.py 中的 Access Key
sed -i '' "s/YOUR_WEB3FORMS_ACCESS_KEY/$ACCESS_KEY/g" rebuild_site_v2.py

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
  echo "📧 测试留言板："
  echo "  部署后访问任意产品页面，填写留言表单"
  echo "  你会在邮箱收到通知"
  echo ""
else
  echo "❌ 网站生成失败"
  exit 1
fi
