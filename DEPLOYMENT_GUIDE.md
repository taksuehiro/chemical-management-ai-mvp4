# AWS EC2 デプロイメントガイド

## 概要
GitHubリポジトリからAWS EC2インスタンスへのコード反映手順

## デプロイ手順

### 1. EC2インスタンスに接続
AWSコンソール → EC2 → インスタンス → 「接続」→ 「EC2 Instance Connect」

### 2. 最新コードの取得と反映

```bash
# アプリケーションディレクトリに移動
cd /home/ubuntu/chemical-mvp5

# 既存のプロセスを停止
pkill -f "python3 app.py"

# 最新のコードを取得
git pull origin main

# 依存関係の確認（必要に応じて）
pip3 install -r requirements.txt

# アプリケーションを再起動
nohup python3 app.py > app.log 2>&1 &

# プロセスが正常に起動したか確認
sleep 5
if pgrep -f "python3 app.py" > /dev/null; then
    echo "✅ アプリケーションが正常に起動しました"
    echo "🌐 URL: http://18.177.174.106:5001"
else
    echo "❌ アプリケーションの起動に失敗しました"
    tail -20 app.log
fi
```

### 3. 静的ファイルの確認

```bash
# PDFファイルの存在確認
ls -la static/samples/*.pdf
```

## ワンライナーでのデプロイ

```bash
cd /home/ubuntu/chemical-mvp5 && pkill -f "python3 app.py" && git pull origin main && nohup python3 app.py > app.log 2>&1 & && sleep 5 && echo "デプロイ完了: http://18.177.174.106:5001"
```

## トラブルシューティング

### プロセスが起動しない場合
```bash
# ログを確認
cat app.log

# ポートが使用中かチェック
sudo lsof -i :5001
```

### PDFファイルが表示されない場合
```bash
# ファイルの存在確認
ls -la static/samples/
```

## 注意事項
- 本番環境ではHTTPS化を検討してください
- 定期的にログを確認してください
- セキュリティグループでポート5001が開放されていることを確認してください 