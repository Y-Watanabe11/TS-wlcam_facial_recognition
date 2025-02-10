import face_recognition
import pickle
import cv2
import os

# 顔画像の保存ディレクトリ
FACE_DIR = "face_database"
ENCODINGS_FILE = "encodings.pkl"

# 登録用データ
known_encodings = []
known_names = []

# ディレクトリ内の画像を処理
for file in os.listdir(FACE_DIR):
    if file.endswith(".jpg") or file.endswith(".png"):
        name = os.path.splitext(file)[0]  
        image_path = os.path.join(FACE_DIR, file)
        
        # 画像を読み込んでエンコーディングを取得
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(name)
            print(f"[INFO] {name} の顔データを登録しました。")
        else:
            print(f"[WARNING] {name} の顔が検出できませんでした。")

# 学習データを保存
data = {"encodings": known_encodings, "names": known_names}
with open(ENCODINGS_FILE, "wb") as f:
    pickle.dump(data, f)

print("[INFO] 顔データベースの作成が完了しました！")
