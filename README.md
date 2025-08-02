# 化学物質管理AI支援サービス

SDS（Safety Data Sheet）からIMDS（International Material Data System）への変換と化学物質相談チャットボットを提供するAI支援サービスです。

## 機能

### SDS→IMDS変換
- PDFファイルのドラッグ&ドロップ対応
- AIによる自動データ抽出
- 抽出結果のAccept/Reject/修正機能
- 4階層IMDS構造でのプレビュー表示
- データ品質情報と総濃度チェック

### 化学物質相談チャットボット
- 有害性、保管方法、廃棄方法などの質問対応
- 代替物質や規制対応の相談サポート

## 技術スタック

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI**: シミュレーション（キーワードマッチング）
- **Deployment**: AWS (Heroku互換)

## セットアップ

### ローカル開発

1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

2. アプリケーションの起動
```bash
python app.py
```

3. ブラウザでアクセス
```
http://localhost:5001
```

### AWSデプロイ

1. Gitリポジトリの作成
```bash
git init
git add .
git commit -m "Initial commit"
```

2. GitHubへのプッシュ
```bash
git remote add origin https://github.com/taksuehiro/chemical-management-ai-mvp5.git
git push -u origin main
```

3. AWS Elastic Beanstalkでのデプロイ
   - AWSコンソールからElastic Beanstalk環境を作成
   - GitHubリポジトリと連携
   - 自動デプロイ設定

## プロジェクト構造

```
MVP5/
├── app.py                 # メインアプリケーション
├── requirements.txt       # Python依存関係
├── Procfile              # Heroku/AWS設定
├── runtime.txt           # Pythonバージョン指定
├── templates/            # HTMLテンプレート
│   ├── index.html       # メインページ
│   └── view_sds.html    # PDF表示ページ
├── static/              # 静的ファイル
│   ├── samples/         # サンプルPDFファイル
│   └── ...
└── uploads/             # アップロードファイル保存
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 