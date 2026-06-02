function showResult(){

    let marks = 8;
    let total = 10;

    document.getElementById("score").innerHTML = marks + " / " + total;

    let status = document.getElementById("status");

    if(marks >= 5){
        status.innerHTML = "Congratulations! You Passed";
        status.style.color = "green";
    }
    else{
        status.innerHTML = "Sorry! You Failed";
        status.style.color = "red";
    }

}