FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# デフォルトコマンド
CMD ["python", "app.py"]

