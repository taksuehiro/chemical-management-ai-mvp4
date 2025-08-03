#!/bin/bash

echo "🚀 MVP5 デプロイ開始..."

# ディレクトリ移動
cd /home/ubuntu/chemical-mvp5

# 既存プロセス停止
echo "📴 既存プロセスを停止中..."
pkill -f "python3 app.py" || true

# 最新コード取得
echo "📥 最新コードを取得中..."
git pull origin main

# 依存関係インストール
echo "📦 依存関係を確認中..."
pip3 install -r requirements.txt

# アプリケーション起動
echo "🚀 アプリケーションを起動中..."
nohup python3 app.py > app.log 2>&1 &

# 起動確認
sleep 5
if pgrep -f "python3 app.py" > /dev/null; then
    echo "✅ デプロイ成功！"
    echo "🌐 URL: http://18.177.174.106:5001"
    echo "📊 プロセスID: $(pgrep -f 'python3 app.py')"
else
    echo "❌ デプロイ失敗"
    echo "📋 ログ:"
    tail -10 app.log
fi 