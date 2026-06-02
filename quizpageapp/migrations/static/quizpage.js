function checkAnswer(){

    let answer =
    document.querySelector('input[name="q1"]:checked');

    let result =
    document.getElementById("result");

    if(answer == null){
        result.innerHTML = "Please select an answer";
        result.style.color = "red";
        return;
    }

    if(answer.value == "Python"){
        result.innerHTML = "Correct Answer";
        result.style.color = "green";
    }
    else{
        result.innerHTML = "Wrong Answer";
        result.style.color = "red";
    }
}