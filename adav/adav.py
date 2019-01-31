from flask import render_template, Flask,request,Response
from keras import models,backend
from PIL import Image
from keras.preprocessing import image
import tensorflow
import numpy as np
import json,base64,datetime,io,locale,os,cv2

#グラフの描写に必要
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import urllib.parse         #描写したグラフをエンコードするのに必要

import calendar

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
blade_model = models.load_model("model/blade_predict.hdf5")

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

    message = predict(getdata)
    if message:    # 異常アリ
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
            if(not hist_matching(cnvString(getdata[HEADER_IDX:]),FILE_PATH_JSONDATA + filename)):   #前回キャプチャした画像と似ていない場合書き込み
                with open(FILE_PATH_JSONDATA + filename, "r") as f:
                    read_json = json.load(f)
                    print("読み込み成功:")
                    read_json[key] = {
                        "imageBynary": imageBynary,
                        "detail" : message,
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
            else:
                return Response(None)

        else:   #ファイルが存在しない場合新規作成
            with open(FILE_PATH_JSONDATA + filename, "w") as f:
                json_data = {
                    key:{
                        "imageBynary": imageBynary,
                        "detail" : message,
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
    fileli = os.listdir(FILE_PATH_JSONDATA)
    list1,list2,list3,list4,list5,list6,list7,list8,list9,list10,list11,list12 = [],[],[],[],[],[],[],[],[],[],[],[]
    for x in fileli:
        if x[0:4] == "2019" and x[4:6] == "01": list1.append(x)
        if x[0:4] == "2019" and x[4:6] == "02": list2.append(x)
        if x[0:4] == "2019" and x[4:6] == "03": list3.append(x)
        if x[0:4] == "2019" and x[4:6] == "04": list4.append(x)
        if x[0:4] == "2019" and x[4:6] == "05": list5.append(x)
        if x[0:4] == "2019" and x[4:6] == "06": list6.append(x)
        if x[0:4] == "2019" and x[4:6] == "07": list7.append(x)
        if x[0:4] == "2019" and x[4:6] == "08": list8.append(x)
        if x[0:4] == "2019" and x[4:6] == "09": list9.append(x)
        if x[0:4] == "2019" and x[4:6] == "10": list10.append(x)
        if x[0:4] == "2019" and x[4:6] == "11": list11.append(x)
        if x[0:4] == "2019" and x[4:6] == "12": list12.append(x)
    filelist = [list1,list2,list3,list4,list5,list6,list7,list8,list9,list10,list11,list12]
    return render_template('filelist.html',filelist=filelist)

#一覧表示年指定
@app.route('/listy', methods=['GET'])
def listy():
    year = request.query_string.decode()
    fileli = os.listdir(FILE_PATH_JSONDATA)
    list1,list2,list3,list4,list5,list6,list7,list8,list9,list10,list11,list12 = [],[],[],[],[],[],[],[],[],[],[],[]
    for x in fileli:
        if x[0:4] == year[6:] and x[4:6] == "01": list1.append(x)
        if x[0:4] == year[6:] and x[4:6] == "02": list2.append(x)
        if x[0:4] == year[6:] and x[4:6] == "03": list3.append(x)
        if x[0:4] == year[6:] and x[4:6] == "04": list4.append(x)
        if x[0:4] == year[6:] and x[4:6] == "05": list5.append(x)
        if x[0:4] == year[6:] and x[4:6] == "06": list6.append(x)
        if x[0:4] == year[6:] and x[4:6] == "07": list7.append(x)
        if x[0:4] == year[6:] and x[4:6] == "08": list8.append(x)
        if x[0:4] == year[6:] and x[4:6] == "09": list9.append(x)
        if x[0:4] == year[6:] and x[4:6] == "10": list10.append(x)
        if x[0:4] == year[6:] and x[4:6] == "11": list11.append(x)
        if x[0:4] == year[6:] and x[4:6] == "12": list12.append(x)
    filelist = [list1,list2,list3,list4,list5,list6,list7,list8,list9,list10,list11,list12]
    return render_template('filelist.html',filelist=filelist)

@app.route('/devil', methods=['GET'])
def devil():
    return render_template('devil.html')

#画像一覧表示
@app.route('/imagelist',methods=['GET'])
def imageList():
    filename = request.query_string.decode()    #リクエストデータをbyte型→文字列変換

    #jsonデータの中身を取り出す
    with open(FILE_PATH_JSONDATA + filename, "r") as f:
        read_json = json.load(f)
        print(read_json)

    return render_template('imagelist.html',read_json=read_json)

#TODO 月毎集計
@app.route('/monthagg',methods=['GET'])
def monthAgg():
    #リクエストデータに応じて年を変更する
    data = request.query_string.decode()    #リクエストデータ（年）を取得

    if(data):   #年が取得できた場合
        year = data
    else:   #リクエストデータがなかった場合
        year = datetime.datetime.today().strftime("%Y") #今年を取得
        year = str(int(year) -1 ) #-1で1年前

    month =[1,2,3,4,5,6,7,8,9,10,11,12]
    agglist = [0,0,0,0,0,0,0,0,0,0,0,0]

    #集計
    filelist = os.listdir(FILE_PATH_JSONDATA)
    for filename in filelist :
        if filename != "dummy.txt" and filename[0:4] == year:
            with open(FILE_PATH_JSONDATA + filename, "r") as f:
                read_json = json.load(f)
                #print(filename[4:6])    #月の部分 "01"～"12"
                idx = int(filename[4:6]) - 1  #0～11まで(1月から12月まで)
                agglist[idx] += len(read_json)   #該当する月の件数を追加

    graph_data = createGraph(month,agglist,year,margin=100,xlabel="MONTH",xmin=0,xmax=12,xmargin=3)  #グラフ生成
    return render_template('month_agg_show.html',graph_data=graph_data,agglist=agglist,month=month,next_year=int(year) + 1,last_year=int(year) - 1)

#TODO 日毎集計
@app.route('/dayagg',methods=['GET'])
def dayAgg():
    #リクエストデータに応じて年を変更する
    data = request.query_string.decode() #リクエストデータ(年月)を取得

    if(data):
        year = data[0:4]
        month = data[4:6]
        if(int(month) == 0):
            year = str(int(year) - 1)
            month = "12"
        elif(int(month) >= 13):
            year = str(int(year) + 1)
            month = "01"
    else:
        year = datetime.datetime.today().strftime("%Y") #今年を取得
        month = datetime.datetime.today().strftime("%m") #今月を取得
        #year = str(int(month) -1 ) #-1で1年前

    agglist = []    #日ごとの検出数
    day =[] #日付を格納する
    title = year + "/" + month
    yearmonth = year + month
    #該当する年月の最終日付を取得する（リストの要素数となる）
    dummy, lastday = calendar.monthrange(int(year),int(month))

    #初期化
    for i in range(lastday):
        agglist.append(0)
        day.append(i+1)

    filelist = os.listdir(FILE_PATH_JSONDATA)
    for filename in filelist :
        if filename != "dummy.txt" and filename[0:4] == year and filename[4:6] == month:
            with open(FILE_PATH_JSONDATA + filename, "r") as f:
                read_json = json.load(f)
                print(filename[6:8])    #月の部分 "01"～"12"
                idx = int(filename[6:8]) - 1  #0～最終日-1
                agglist[idx] += len(read_json)   #

    #print(agglist)
    graph_data = createGraph(day,agglist,title,10,"DAY",1,lastday,7)
    return render_template('day_agg_show.html',graph_data=graph_data,agglist=agglist,day=day,last_month=int(yearmonth) - 1,next_month=int(yearmonth) + 1)

def predict(data):
    """
    データの異常有無を予測する。
    異常がある場合 対応したメッセージ を,無い場合 空文字列 を返す
    """
    ret = ""
    global graph
    with graph.as_default():
        # 画像整形種別の定義
        convert_type = {3:"RGB",4:"RGBA"}

        # 姿勢判定用モデルの入力形式取得
        down_input_form = down_model.get_layer(index=0).get_config()["batch_input_shape"][:0:-1]
        # 画像を整形する
        img_buf = io.BytesIO(base64.decodestring(data[HEADER_IDX:]))
        img = Image.open(img_buf)
        img = img.convert(convert_type[down_input_form[0]])
        img = img.resize(down_input_form[1:])
        # 画像をnumpy配列にする
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        # 予測させる
        features = down_model.predict(x)
        if features[0,0] == 1:
            ret += "倒れている人を検出しました。<br>"

        # 凶器判定用モデルの入力形式取得
        blade_input_form = blade_model.get_layer(index=0).get_config()["batch_input_shape"][:0:-1]
        # 入力形式が異なる場合画像再整形
        if down_input_form != blade_input_form:
            img_buf = io.BytesIO(base64.decodestring(data[HEADER_IDX:]))
            img = Image.open(img_buf)
            img = img.convert(convert_type[blade_input_form[0]])
            img = img.resize(blade_input_form[1:])
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
        # 予測させる
        features = blade_model.predict(x)
        if features[0,0] == 1:
            ret += "凶器を検出しました。<br>"
    return ret

def createGraph(xlist,ylist,title,margin,xlabel,xmin,xmax,xmargin):
    """
    :param xlist: xlist:x軸に使用するList
    :param ylist: y軸に使用するList
    :param title: グラフタイトルString
    :param margin: y軸の余白int
    :param xlabel: x軸のラベルString
    :param xmin: x軸の下限値int
    :param xmax: x軸の上限値int
    :param xmargin: x軸メモリの余白
    :return:
    """

    # 参考URL
    #【http://kaisk.hatenadiary.com/entry/2014/11/30/163016】
    #【https://stats.biopapyrus.jp/python/params.html】
    #【http://python-remrin.hatenadiary.jp/entry/2017/05/27/114816】
    #【https://pythonmemo.hatenablog.jp/entry/2018/04/22/204614】
    #【http://d.hatena.ne.jp/y_n_c/20091122/1258842406】
    #【https://qiita.com/5t111111/items/3d9efdbcc630daf0e48f】
    #【http://k-kuro.hatenadiary.jp/entry/20180213/p1】
    #【https://hopita.hatenablog.com/entry/2019/01/03/230121】

    #カラーコードの定義
    COLOR_WHITE = "#FFFFFF"
    COLOR_BACKGROUND = "#333333"
    COLOR_GRID = "#CFCFCF"

    y_margin = max(ylist) - max(ylist) % margin + margin    #y軸の余白を最高値に合わせて取る
    x = np.array(xlist) #x座標:1月～12月
    y = np.array(ylist) #y座標:実際の集計数

    fig, ax = plt.subplots()

    plt.tick_params(length=0)   # メモリを消す
    plt.ylim(ymin=0,ymax=y_margin)  # y軸の範囲を設定
    plt.xticks(np.arange(xmin, xmax + 1, xmargin))
    plt.xlabel(xlabel,color=COLOR_WHITE) # x軸ラベル
    plt.ylabel('DETECTION',color=COLOR_WHITE) # y軸ラベル

    fig.patch.set_facecolor(COLOR_BACKGROUND)  # 図全体の背景色
    ax.set_title(title,color=COLOR_WHITE) # グラフタイトル
    ax.plot(x,y, linestyle = '-',marker="D",color="#40AAEF")    # グラフを描写
    ax.patch.set_facecolor(COLOR_BACKGROUND)  # subplotの背景色

    #グラフの枠線の描写
    ax.spines["right"].set_color("none")  # 右消し
    ax.spines["top"].set_color("none")    # 上消し
    ax.spines["left"].set_color(COLOR_WHITE)   # 左白線
    ax.spines["bottom"].set_color(COLOR_WHITE) # 下白線

    #グリッドの描写
    ax.xaxis.grid(True, which = 'major', linestyle = '-', color = COLOR_GRID)
    ax.yaxis.grid(True, which = 'major', linestyle = '-', color = COLOR_GRID)

    #メモリの数字の色を変更する
    for item in ax.get_xticklabels():
        item.set_color(COLOR_WHITE)

    for item in ax.get_yticklabels():
        item.set_color(COLOR_WHITE)

    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    data = buf.getvalue()
    return urllib.parse.quote(data)

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


#引数のtarget_binaryは画像のバイナリだけ
#引数のfilenameには、最新のjsonファイル
def hist_matching(target_binary,filename):
    #比較して80％以上似ていたらTrue
    #似てないならFalse

    IMG_SIZE = (200, 200) #画像サイズの指定

    with open(filename, "r") as f:
        read_json = json.load(f)

    #比較対象の画像をバイナリから画像データにする作業
    #バイナリデータ <- base64でエンコードされたデータ
    img_binary = base64.b64decode(target_binary)
    jpg=np.frombuffer(img_binary,dtype=np.uint8)
    #raw image <- jpg　
    target_img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)

    #jsonファイル内の最新の画像をバイナリから画像データに変換する作業
    key = sorted(read_json.keys())[len(read_json.keys()) - 1] #jsonファイル内の一番最後のKeyを持ってきてる
    img_base64 = read_json[key]["imageBynary"][HEADER_IDX:] # バイナリのみ抽出

    #バイナリデータ <- base64でエンコードされたデータ
    img_binary = base64.b64decode(img_base64)
    jpg=np.frombuffer(img_binary,dtype=np.uint8)
    #raw image <- jpg　
    comparing_img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)

    #ここから比較する作業
    target_img = cv2.resize(target_img, IMG_SIZE)  #比較元画像のサイズを200,200にリサイズする
    target_hist = cv2.calcHist([target_img], [0], None, [256], [0, 256]) #画像の色相分布行列化


    comparing_img = cv2.resize(comparing_img, IMG_SIZE) #比較先画像のサイズを200,200にリサイズする
    comparing_hist = cv2.calcHist([comparing_img], [0], None, [256], [0, 256]) #画像の色相分布行列化

    ret = cv2.compareHist(target_hist, comparing_hist, 0) #比率をだす

    #80％以上似ていたらTrue 以下ならFalse
    print(ret)
    if ret >= 0.8:
        return True
    return False


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8087, debug=True)
