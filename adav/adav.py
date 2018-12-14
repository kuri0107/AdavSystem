from flask import render_template, Flask,request,Response
from keras import models,backend
from PIL import Image
from keras.preprocessing import image
import numpy as np
import json,base64,datetime,io,locale,os
app = Flask(__name__)

# ファイルの拡張子の定義
FILE_FORMAT_PNG = ".png"
FILE_FORMAT_JPEG = ".jpeg"
FILE_FORMAT_JSON = ".json"

# JPEGイメージヘッダ部の終端座標
HEADER_IDX = 23
START_BYTE_IDX = 2
END_BYTE_IDX = 1

# 保存先のパス
FILE_PATH_CAPTURE = "static/capture/"
FILE_PATH_JSONDATA = "static/jsondata/"

locale.setlocale(locale.LC_ALL, '')

# トップページへの遷移
@app.route('/')
def top():
    return render_template('top.html')

# メインページへの遷移
@app.route('/main', methods=['GET'])
def display():
    return render_template('main.html')

# ajax通信を用いてキャプチャした画像を送信し分析した結果を返す
@app.route('/capture',methods=['POST'])
def capture():
    # 画像データのリクエスト
    getdata = request.data

    if predict(getdata):    # 異常アリ
        #TODO 分析した結果、異常があった場合サーバに画像を保存

        # captureフォルダに保存
        # ファイル名を日時にする
        # date = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")

        # JPEG
        # filename = str(date) + FILE_FORMAT_JPEG

        # PNG
        # filename = str(date) + FILE_FORMAT_PNG

        #JSON
        filename = datetime.datetime.today().strftime("%Y%m%d") + FILE_FORMAT_JSON
        #キー値として日付を設定
        key = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
        #日本語で日付を設定
        date = datetime.datetime.today().strftime("%Y年%m月%d日%H時%M分%S秒")

        # with open(FILE_PATH + filename, "wb") as f:
        #      f.write(base64.decodestring(getdata[HEADER_IDX:]))

        imageBynary = str(getdata)[START_BYTE_IDX:len(str(getdata))-END_BYTE_IDX]

        #jsonファイルに書き込み
        if os.path.isfile(FILE_PATH_JSONDATA + filename):   #jsonファイルが存在するかどうか
            with open(FILE_PATH_JSONDATA + filename, "r") as f:
                read_json = json.load(f)
                print("読み込み成功:")
                read_json[key] = {
                    "imageBynary": imageBynary,
                    "detail" : "詳細データ",
                    "date" : date
                }
            with open(FILE_PATH_JSONDATA + filename, "w") as f:
                json.dump(read_json,f)
                print("書き込み完了")
        else:   #ファイルが存在しない場合新規作成
            with open(FILE_PATH_JSONDATA + filename, "w") as f:
                json_data = {
                    key:{
                        "imageBynary": imageBynary,
                        "detail" : "詳細データ",
                        "date" : date
                    }
                }
                json.dump(json_data,f)
                print("新規で書き込み完了")

        #取得したバイナリを文字列型に変換
        #先端のb'と終端の'を取り除いて返す
        #str(getdata) → b'XXXX...X'
        #str(getdata)[2:len(str(getdata))-1] → XXXX...X
        retdata = [str(getdata)[START_BYTE_IDX:len(str(getdata))-END_BYTE_IDX]]

        #base64のバイナリデータをjson形式でレスポンスとして返す
        return Response(json.dumps(retdata))
    else:   # 異常ナシ
        return Response()

def predict(data):
    """
    データの異常有無を予測する。
    異常がある場合 True ,無い場合 False を返す
    """
    # 画像整形種別の定義
    convert_type = {3:"RGB",4:"RGBA"}

    # 姿勢判定用モデルのロード
    model = models.load_model("model/down_predict.hdf5")
    input_form = model.get_layer(index=0).get_config()["batch_input_shape"]
    # 画像を整形する
    img_buf = io.BytesIO(base64.decodestring(data[HEADER_IDX:]))
    img = Image.open(img_buf)
    img = img.convert(convert_type[input_form[3]])
    img = img.resize(input_form[1:3])
    # 画像をnumpy配列にする
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    # 予測させる
    features = model.predict(x)
    backend.clear_session()
    # 予測結果による処理
    if features[0,0] == 1:
        # 異常時
        return True
    else:
        # 正常時・予測不能時
        return False

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
