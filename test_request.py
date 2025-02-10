import requests
from requests.auth import HTTPDigestAuth
import cv2
import numpy as np
import re

# 📌 カメラの設定 (Digest 認証)
CAMERA_IP = "" #カメラのIPアドレス
USERNAME = ""  # Digest認証のユーザー名
PASSWORD = ""  # Digest認証のパスワード(初期設定はMACID)
URL = f"http://{CAMERA_IP}/snapshot.cgi" #カメラの画像データのURLの場所

print("[DEBUG] 画像取得テスト開始")

try:
    session = requests.Session()
    session.auth = HTTPDigestAuth(USERNAME, PASSWORD)

    print("[DEBUG] GETリクエストを送信")
    response = session.get(URL, timeout=5, stream=True)  

    print(f"[DEBUG] HTTPレスポンスコード: {response.status_code}")

    if response.status_code == 200:
        print("[INFO] 画像の取得に成功")

        boundary = b"--myboundary"
        buffer = b""

        for chunk in response.iter_content(chunk_size=4096):
            buffer += chunk

            
            start = buffer.find(b'\xff\xd8') 
            end = buffer.find(b'\xff\xd9')    

            if start != -1 and end != -1:
                jpeg_data = buffer[start:end+2] 
                print(f"[DEBUG] 画像サイズ: {len(jpeg_data)} バイト")

                
                img_array = np.asarray(bytearray(jpeg_data), dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if frame is None:
                    print("[ERROR] 画像のデコードに失敗しました")
                else:
                    cv2.imwrite("debug_image_fixed.jpg", frame)
                    print("[INFO] 画像を debug_image_fixed.jpg に保存しました")
                    break  
    else:
        print(f"[ERROR] 画像の取得に失敗: HTTP {response.status_code}")

except requests.exceptions.Timeout:
    print("[ERROR] 画像の取得がタイムアウトしました")
except requests.exceptions.ConnectionError:
    print("[ERROR] ネットワーク接続エラーが発生しました")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] その他のリクエストエラー: {e}")
