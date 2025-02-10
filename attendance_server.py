from flask import Flask, send_file, jsonify
import os
import csv

# Flask サーバーの設定
app = Flask(__name__)

# 📌 出席記録ファイルのパス
ATTENDANCE_FILE = "attendance.csv"

# 📌 ルートページ（出席データの一覧を表示）
@app.route("/")
def home():
    if not os.path.exists(ATTENDANCE_FILE):
        return jsonify({"error": "出席データが存在しません"}), 404

    
    attendance_data = []
    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            attendance_data.append(row)

    html = "<h2>出席データ一覧</h2><table border='1'><tr><th>日付</th><th>名前</th><th>時間</th></tr>"
    for row in attendance_data:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    html += "</table>"

    
    html += '<br><a href="/download">📥 出席データをダウンロード</a>'

    return html

# 📌 出席データをダウンロードするエンドポイント
@app.route("/download")
def download():
    if not os.path.exists(ATTENDANCE_FILE):
        return jsonify({"error": "出席データが存在しません"}), 404

    return send_file(ATTENDANCE_FILE, as_attachment=True, download_name="attendance.csv")

# 📌 サーバー起動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
