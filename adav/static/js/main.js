$(function(){
    $("button").click(function(){
        $("tr#capture").remove();
    });
});

//webカメラ
//ajaxで5秒ごとに画像データを送信
$(function(){
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || window.navigator.mozGetUserMedia;
    window.URL = window.URL || window.webkitURL;

    var video = document.getElementById('myVideo');
    var localStream = null;
    navigator.getUserMedia({video: true, audio: false},
    function(stream) {
        console.log(stream);
        //video.src = window.URL.createObjectURL(stream);

        //createObjectURLについて
        //https://www.fxsitecompat.com/ja/docs/2018/url-createobjecturl-no-longer-accepts-mediastream-as-argument/

        video.srcObject = stream
        setInterval(function() {
        var canvas = document.getElementById('canvas');

        //canvasの描画モードを2sに
        var ctx = canvas.getContext('2d');
        var img = document.getElementById('img');

        //videoの縦幅横幅を取得
        var w = video.offsetWidth;
        var h = video.offsetHeight;

        //同じサイズをcanvasに指定
        canvas.setAttribute("width", w);
        canvas.setAttribute("height", h);

        //canvasにコピー
        ctx.drawImage(video, 0, 0, w, h);

        //imgにjpeg形式で書き出し
        var base64 = this.canvas.toDataURL('image/jpeg');

        //imgにpng形式で書き出し
        //var base64 = this.canvas.toDataURL('image/png');

        $.ajax({
            type: 'POST',
            url: '/capture',
            data: base64,
            contentType: 'image/jpeg',

            //サーバからの返送データ(json)を受け取る
            success: function(data) {
                console.log("通信成功");
                console.log("dataの値:"+data);
                if(data !== ""){
                    var bar_list = $.parseJSON(data);
                    //jsonの要素数分、リストに追加
                    //for (var i in bar_list) {
                    //console.log(bar_list[i])
                    //canvasと同じ横と縦をセット
                    //var html= "<tr id='capture'><td><form action='/act' method='post' target='_blank'><input type='image' src='" + bar_list[0] + "' width='320' height='240' value='"+ bar_list[1] + "'></form></td></tr>";
                    var html = "<tr id='capture'><td><a href='/act?" + bar_list[1] + "' target='_blank'><img src='" + bar_list[0] +"' width='320' height='240'></a></td></tr>";
                    //$("#capture_table").append(html);
                    $("#capture_table:first").after(html);
                    console.log("キーの値"+bar_list[1]);
                }else{
                    console.log("判定の結果正常です。");
                }
            }
        });
    }, 5000);
    },function(err) { // for error case
    console.log(err);
    });
});
