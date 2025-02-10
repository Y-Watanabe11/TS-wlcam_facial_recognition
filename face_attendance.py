import cv2
import requests
import numpy as np
import face_recognition
import pickle
import csv
import os
import time
from datetime import datetime
from requests.auth import HTTPDigestAuth

# 📌 カメラの設定 (Digest 認証)
CAMERA_IP = "" #カメラのIPアドレス
USERNAME = ""  # Digest認証のユーザー名
PASSWORD = ""  # Digest認証のパスワード(初期設定はMACID)
URL = f"http://{CAMERA_IP}/snapshot.cgi"

# 📌 出席記録用ファイル
ATTENDANCE_FILE = "attendance.csv"
LOG_FILE = "attendance.log"

print("[DEBUG] プログラム開始")

# 📌 顔データベースをロード
try:
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)

    known_encodings = data["encodings"]
    known_names = data["names"]
    print(f"[DEBUG] 顔データベースをロード: {len(known_encodings)} 人")
except Exception as e:
    print(f"[ERROR] 顔データベースのロードに失敗: {e}")
    exit(1)

# 📌 出席リストを取得（1日に1回のみ記録）
def load_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    attendance_list = set()

    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == today:
                    attendance_list.add(row[1])
    print(f"[DEBUG] 今日の出席者リストをロード: {len(attendance_list)} 人")
    return attendance_list

# 📌 出席記録を保存
def mark_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today, name, current_time])

    log_message = f"{datetime.now()} [INFO] {name} の出席を記録: {current_time}\n"
    print(log_message.strip())

    # 📌 ログをファイルに保存
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_message)

# 📌 メインループ（カメラ映像取得 & 顔認識）
attendance_today = load_attendance()

while True:
    try:
        print("[DEBUG] 画像取得を開始")

        session = requests.Session()
        session.auth = HTTPDigestAuth(USERNAME, PASSWORD)

        # 📌 ネットワークエラー時のリトライ機能（最大5回）
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = session.get(URL, timeout=10, stream=True)  # タイムアウトを 10 秒に延長
                break  
            except requests.exceptions.Timeout:
                print(f"[WARNING] タイムアウト発生（試行 {attempt+1}/{max_retries}）")
                time.sleep(3)
            except requests.exceptions.ConnectionError:
                print(f"[WARNING] 接続エラー（試行 {attempt+1}/{max_retries}）")
                time.sleep(3)
        else:
            print("[ERROR] 最大リトライ回数を超えました。スキップします。")
            continue  

        print(f"[DEBUG] HTTPレスポンスコード: {response.status_code}")

        if response.status_code == 200:
            print("[INFO] 画像の取得に成功")

            buffer = b""
            for chunk in response.iter_content(chunk_size=16384):  #
                buffer += chunk

                start = buffer.find(b'\xff\xd8')  
                end = buffer.find(b'\xff\xd9')   

                if start != -1 and end != -1:
                    jpeg_data = buffer[start:end+2]
                    jpeg_size = len(jpeg_data)
                    print(f"[DEBUG] 取得した JPEG 画像サイズ: {jpeg_size} バイト")

                    if jpeg_size < 10000:  
                        print("[ERROR] 取得した JPEG データが小さすぎます。スキップします。")
                        continue

                    img_array = np.asarray(bytearray(jpeg_data), dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    if frame is None:
                        print("[ERROR] 画像のデコードに失敗しました。スキップします。")
                        continue

                    print("[DEBUG] 画像のデコード成功")

                    # 📌 OpenCVのBGR形式をRGBに変換
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # 📌 顔の検出
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                    print(f"[INFO] 顔検出数: {len(face_locations)}")

                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        matches = face_recognition.compare_faces(known_encodings, face_encoding)
                        name = "Unknown"

                        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index]:
                            name = known_names[best_match_index]

                            if name not in attendance_today:
                                mark_attendance(name)
                                attendance_today.add(name)

                        print(f"[INFO] 認識した顔: {name}")

                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.imshow("Live Face Attendance", frame)

                    break  

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] ネットワークエラー: {e}")
        time.sleep(5)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
