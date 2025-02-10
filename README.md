# TS-wlcam_facial_recognition
IO-DATA製のTS-WLCAMを用いた顔認証システムのコードを書きました。

使用している製品  
[IO DATA TS-WLCAM](https://www.iodata.jp/product/lancam/lancam/ts-wlcam/)

実行環境：  
OS:MAC sonoma  
python3.10.2  
(serverコード以外はpython3.13で動作確認済み)

# 使用方法

1. face_databaseディレクトリにサンプルの顔写真を「顔と結びつける名前.png」の形式でおき、face_charge.pyを実行します。
2. 読み込みが完了すると、pngファイルの名前+読み込み完了と出てきます。これで登録完了です。
3. test_request.pyを使用することで、カメラとの接続がうまくいっているかを確認してください
4. 接続がうまくいっていることを確認したのち、face_attendance.pyを実行すると顔認証がスタートします。
