var countUpValue = 0;

//カウントアップする関数 countUp の定義
function countUp(){
    countUpValue++;
    if (countUpValue == 3){
    countUpValue = 0;
    location.href = "/devil";
    }
}
function countReset(){
    countUpValue = 0;
}


