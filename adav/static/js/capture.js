//ウェブカメラで撮影
//TODO htmlへのスクリプトの埋め込みは動くと思われるが、jsファイルに書き上げた場合うまく動かない

//navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || window.navigator.mozGetUserMedia;
//window.URL = window.URL || window.webkitURL;
//
//var video = document.getElementById('myVideo');
//var localStream = null;
//navigator.getUserMedia({video: true, audio: false},
//function(stream) {
//    console.log(stream);
//    video.src = window.URL.createObjectURL(stream);
//    setInterval(function() {
//    var canvas = document.getElementById('canvas');
//
//    //canvasの描画モードを2sに
//    var ctx = canvas.getContext('2d');
//    var img = document.getElementById('img');
//
//    //videoの縦幅横幅を取得
//    var w = video.offsetWidth;
//    var h = video.offsetHeight;
//
//    //同じサイズをcanvasに指定
//    canvas.setAttribute("width", w);
//    canvas.setAttribute("height", h);
//
//    //canvasにコピー
//    ctx.drawImage(video, 0, 0, w, h);
//
//    //imgにpng形式で書き出し
//    img.src = canvas.toDataURL('image/jpg');
//
//    const request = new XMLHttpRequest();
//    request.open("GET", `https://url/${img.src}`);
//    request.send();
//    }, 5000);
//},function(err) { // for error case
//    console.log(err);
//});

//非同期通信でサーバに画像を送信し、異常があった場合表示する
//$(function() {
//  $("#exajax").click(function() {
//    reader = new FileReader()
//    var jpeg
//    reader.onload = function() {
//      jpeg = reader.result
//      $.ajax({
//        type: 'POST',
//        url: '/capture',
//        data: jpeg,
//        contentType: 'image/jpeg',
//        //サーバからの返送データ(json)を受け取る
//        success: function(data) {
//          console.log("通信成功");
//          console.log("dataの値"+data);
//          var bar_list = $.parseJSON(data);
//          //jsonの要素数分、リストに追加
//          for (var i in bar_list) {
//            console.log(bar_list[i])
//            $("img").attr("src", bar_list[i]);
//          }
//        }
//      });
//    }
//    reader.readAsDataURL($("#imgfile")[0].files[0])
//  });
//});
