import os
import json
import gspread
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Googleスプレッドシートの設定
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"  # スプレッドシートIDを設定
SHEET_NAME = "SlackActions"  # 対象のシート名

# Google認証情報ファイルのパス（環境変数として設定する）
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Googleスプレッドシートに接続
def connect_to_sheet():
    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_JSON,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return sheet

@app.route("/", methods=["POST"])
def slack_action_handler():
    # Slackからのリクエストをパース
    payload = json.loads(request.form["payload"])
    
    # トークン検証（必要に応じて設定）
    verification_token = "YOUR_VERIFICATION_TOKEN"
    if payload["token"] != verification_token:
        return jsonify({"text": "Invalid token"}), 403

    # ボタンアクションの処理
    user = payload["user"]["name"]  # ボタンを押したユーザー名
    action_value = payload["actions"][0]["value"]  # ボタンの値

    # スプレッドシートに出力
    sheet = connect_to_sheet()
    row = [user, action_value, payload["callback_id"], payload["message"]["text"]]
    sheet.append_row(row)

    # Slackにレスポンスを返す
    return jsonify({"text": f"{user} さんが '{action_value}' を選択しました。データをスプレッドシートに記録しました。"})

# Cloud Functionsのエントリポイント
def main(request):
    return app(request)