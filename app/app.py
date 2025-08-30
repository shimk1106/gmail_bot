import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from openai import OpenAI

# OpenAIクライアント
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Gmail APIスコープ
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # ブラウザ不要
        )

        auth_url, _ = flow.authorization_url(prompt='consent')
        print("下記URLをコピーしてブラウザで開き、認証コードを取得してください:\n")
        print(auth_url)
        code = input("\n認証コードを入力してください: ")
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
        print("認証完了！ token.json が作成されました。")

    return build('gmail', 'v1', credentials=creds)

def list_unreplied_messages(service, user_id="me"):
    results = service.users().messages().list(userId=user_id, q="in:inbox -from:me").execute()
    return results.get('messages', [])

def get_message_detail(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = msg['payload']
    headers = payload.get("headers")
    subject = sender = None
    for h in headers:
        if h['name'] == 'Subject':
            subject = h['value']
        if h['name'] == 'From':
            sender = h['value']

    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode("utf-8")
                break
    else:
        data = payload['body']['data']
        body = base64.urlsafe_b64decode(data).decode("utf-8")

    return subject, sender, body

def classify_with_chatgpt(subject, sender, body):
    text = f"件名: {subject}\n差出人: {sender}\n本文:\n{body[:1000]}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはメールアシスタントです。"},
            {"role": "user", "content": f"以下のメールが『重要で返信が必要』かどうかを判定してください。重要かどうかは売り込みや広告ではなく、人間がアクションを求めているものやサービスからの期限付きの更新登録など。結果の1行目に「重要で確認・返信が必要:」に続いてYesかNoを記載してください。2行目以降に要約を50文字以内で書いてください。\n\n{text}"}
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    service = get_gmail_service()
    messages = list_unreplied_messages(service)

    if not messages:
        print("📭 未返信メールはありません。")
        return

    print(f"未返信メール数: {len(messages)}\n")
    for m in messages[:20]:
        subject, sender, body = get_message_detail(service, m['id'])
        result = classify_with_chatgpt(subject, sender, body)

        first_line = result.split("\n")[0]
        is_important = "Yes" in first_line

        if is_important:
            print("------")
            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print(result)  # 重要メールは要約も表示
            print()
        else:
            # 重要でないメールは簡単に表示
            print(f"Subject: {subject}")
            print(f"重要メール: No\n")

if __name__ == '__main__':
    main()

