from flask import render_template, Flask,request,Response
from keras import models,backend
from PIL import Image
from keras.preprocessing import image
import tensorflow
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
FILE_PATH_IMAGES = "static/capture/"
FILE_PATH_JSONDATA = "static/jsondata/"

# モデル準備
graph = tensorflow.get_default_graph()
down_model = models.load_model("model/down_predict.hdf5")
#blade_model = models.load_model("model/blade_predict.hdf5")

#日付を日本語で入れるのに必要
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
        #ファイル名を設定
        #filename = createFileName(FILE_FORMAT_JPEG) #JPEGで保存
        #filename = createFileName(FILE_FORMAT_PNG) #PNGで保存
        filename = createFileName(FILE_FORMAT_JSON) #JSONで保存

        #キー値として日付を設定
        key = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")

        #日本語で日付を設定
        date = datetime.datetime.today().strftime("%Y年%m月%d日%H時%M分%S秒")

        #ヘッダ部を取り除き、画像を保存
        # with open(FILE_PATH_IMAGES + filename, "wb") as f:
        #      f.write(base64.decodestring(getdata[HEADER_IDX:]))

        #imageBynary = str(getdata)[START_BYTE_IDX:len(str(getdata))-END_BYTE_IDX]
        imageBynary = cnvString(getdata)

        #TODO 読み込み失敗時の処理
        #jsonファイルに書き込み
        if os.path.isfile(FILE_PATH_JSONDATA + filename):   #jsonファイルが存在する場合
            # try:
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
            # except:
            # with open(FILE_PATH_JSONDATA+ filename, "w") as f:
            #     json_data = {
            #         key:{
            #             "imageBynary": imageBynary,
            #             "detail" : "詳細データ",
            #             "date" : date
            #         }
            #     }
            #     json.dump(json_data,f)
            # print("ファイルに問題があるため、新規作成します。")
            # pass

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
        retdata = [cnvString(getdata),key]
        #base64のバイナリデータをjson形式でレスポンスとして返す
        return Response(json.dumps(retdata))
    else:   # 異常ナシ
        return Response(None)

#詳細表示
@app.route('/act',methods=['POST',"GET"])
def details():
    # form = cgi.FieldStorage()
    # key = form["key"].value
    #key = str(str(request.query_string))[START_BYTE_IDX:len(str(str(request.query_string)))-END_BYTE_IDX]
    #key = form.getvalue('im')
    key = request.query_string.decode()
    print(type(key))
    print(key)

    #今日のファイル名を探している
    #filename = datetime.datetime.today().strftime("%Y%m%d") + FILE_FORMAT_JSON
    filename = key[:8] + FILE_FORMAT_JSON   #keyの日付のファイル名を設定
    print("ファイル名:"+filename)

    if os.path.isfile(FILE_PATH_JSONDATA + filename):   #jsonファイルが存在するかどうか
            with open(FILE_PATH_JSONDATA + filename, "r") as f:
                read_json = json.load(f)
                #html = 'act.html'.format(read_json[key].date,read_json[key].imageBynary,read_json[key].detail)
                # print(type(html))
                f.close()

                zi = read_json[key]

                #img_binarystream = io.BytesIO(zi["imageBynary"].encode('utf-8'))、

                #PILイメージ <- バイナリーストリーム
                #img_pil = Image.open(img_binarystream)
            #keyの日付、画像データ、詳細情報を返す
            return render_template("act.html",a=zi["date"],b=zi["imageBynary"],c=zi["detail"])#,a=read_json[key].date,b=read_json[key].imageBynary,c=read_json[key].detail)
    else:
        print("error:ファイルが存在しません")
    return None

#一覧表示
@app.route('/list', methods=['GET'])
def list():
    filelist = os.listdir(FILE_PATH_JSONDATA)
    return render_template('filelist.html',filelist=filelist)

#画像一覧表示
@app.route('/imagelist',methods=['GET'])
def imageList():
    filename = request.query_string.decode()    #リクエストデータをbyte型→文字列変換

    #jsonデータの中身を取り出す
    with open(FILE_PATH_JSONDATA + filename, "r") as f:
        read_json = json.load(f)
        print(read_json)

    return render_template('imagelist.html',read_json=read_json)

def predict(data):
    """
    データの異常有無を予測する。
    異常がある場合 True ,無い場合 False を返す
    """
    global graph
    with graph.as_default():
        # 画像整形種別の定義
        convert_type = {3:"RGB",4:"RGBA"}

        # 姿勢判定用モデルの入力形式取得
        down_input_form = down_model.get_layer(index=0).get_config()["batch_input_shape"]
        # 画像を整形する
        img_buf = io.BytesIO(base64.decodestring(data[HEADER_IDX:]))
        img = Image.open(img_buf)
        img = img.convert(convert_type[down_input_form[3]])
        img = img.resize(down_input_form[1:3])
        # 画像をnumpy配列にする
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        # 予測させる
        features = down_model.predict(x)
        if features[0,0] == 1:
            return True
        else:
            # 正常時・予測不能時
            return False

def cnvString(bynary):
    """
    バイナリ型を文字列型に変換
    先端のb'と終端の'を取り除いて返す
    str(getdata) → b'XXXX...X'
    str(getdata)[2:len(str(getdata))-1] → XXXX...X
    :param bynary:
    :return: string
    """
    s_bynary = str(bynary)
    return s_bynary[START_BYTE_IDX:len(s_bynary)-END_BYTE_IDX]

def createFileName(fileformat):
    """
    今日の日付でファイル名を設定する。
    :param fileformat: ファイル形式
    :return:ファイル名
    """
    return datetime.datetime.today().strftime("%Y%m%d") + fileformat

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8081, debug=True)
