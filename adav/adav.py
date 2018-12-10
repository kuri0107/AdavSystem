from flask import render_template, Flask,request,Response
import json,base64,datetime
app = Flask(__name__)

# ファイルの拡張子の定義
FILE_FORMAT_PNG = ".png"
FILE_FORMAT_JPEG = ".jpeg"

# 保存先のパス
FILE_PATH = "static/images/capture"

#トップページへの遷移
@app.route('/')
def top():
    return render_template('top.html')

#メインページへの遷移
@app.route('/main', methods=['GET'])
def display():
    return render_template('main.html')

#ajax通信を用いてキャプチャした画像を送信し分析した結果を返す
@app.route('/capture',methods=['POST'])
def capture():
    #画像データのリクエスト
    getdata = request.data

    #TODO 分析した結果異常があった場合サーバに画像を保存

    #ファイル名を日時にする
    date = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
    # print("日付型" + date)

    #JPEG
    #filename = str(date) + FILE_FORMAT_JPEG

    #PNG
    filename = str(date) + FILE_FORMAT_PNG

    # print("ファイル名" + filename)


    # with open(FILE_PATH + filename, "wb") as f:
    #      f.write(base64.decodestring(getdata))

    #TODO 分析した結果異常なデータを返す


    #取得したバイナリを文字列型に変換
    #先端のb'と終端の'を取り除いて返す
    #str(getdata) → b'XXXX...X'
    #str(getdata)[2:len(str(getdata))-1] → XXXX...X
    retdata = [str(getdata)[2:len(str(getdata))-1]]
    #base64のバイナリデータをjson形式でレスポンスとして返す
    return Response(json.dumps(retdata))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
