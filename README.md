# gmail_bot
# Gmail 未返信メール判定 Bot (ChatGPT + Docker)

このプロジェクトは、**Gmail の未返信メールを取得して ChatGPT による重要判定・要約** を行う Python スクリプトです。  
Docker 環境でブラウザを使わずに認証でき、簡単に実行できます。

---

## 特徴

- Gmail API から未返信メールを取得
- ChatGPT で「重要で返信が必要か」を判定
- 重要メールのみ要約を出力
- Docker コンテナ内でもブラウザ不要で認証可能
- token.json に認証情報を保存し、再認証不要

---

## 前提条件

- Docker / Docker Compose がインストールされていること
- Google Cloud で Gmail API 用の OAuth クライアントを作成済み
- `credentials.json` を取得済み
- OpenAI API Key を取得済み

---

## ディレクトリ構成

gmail-bot/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app.py
├── credentials.json ← Google Cloud から取得
└── token.json ← 初回認証後に自動生成

yaml
コードをコピーする

---

## 設定手順

1. `credentials.json` をプロジェクト直下に配置
2. `.env` または環境変数で OpenAI API Key を設定

```bash
export OPENAI_API_KEY="sk-xxxx..."
Docker イメージをビルド

bash
コードをコピーする
docker-compose build
コンテナを実行

bash
コードをコピーする
docker-compose run --rm gmail-bot
初回実行時のみコンソールに URL が表示されるので、ホストブラウザで開いて認証コードをコピー → コンソールに貼る

token.json が作成され、次回以降は自動で認証されます

