from flask import render_template, Flask,request,Response
import json,base64

app = Flask(__name__)

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
    #TODO ファイルする保存名を日時にする
    with open("static/images/input.jpeg", "wb") as f:
        f.write(base64.decodestring(getdata))

    #先端のb'と終端の'を取り除いて返す
    #str(getdata) → b'XXXX...X'
    #str(getdata)[2:len(str(getdata))-1] → XXXX...X
    retdata = [str(getdata)[2:len(str(getdata))-1]]

    #TODO 分析した結果異常なデータを返す

    #base64のバイナリデータをjson形式でレスポンスとして返す
    return Response(json.dumps(retdata))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
