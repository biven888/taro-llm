var ws = new WebSocket("ws://" + location.host + "/ws");
var chat = {model: document.getElementById("model").value, messages: []};
var isDone = true;

ws.onopen = function() {
    console.log("Соединение установлено");
};

ws.onclose = function(event) {
    if (event.wasClean) {
        console.log('Соединение закрыто чисто');
    } else {
        console.log('Обрыв соединения'); // например, "убит" процесс сервера
    }
    console.log('Код: ' + event.code + ' причина: ' + event.reason);
};

ws.onmessage = function(event) {
    const answer = document.getElementById("answer");
    const timer = document.getElementById("timer");
    timer.style.display = "none";

    if (event.data == "assistant_message_done") {
        isDone = true;
        answer.innerHTML = answer.innerHTML.replace("<think>", "<details><summary></summary>").replace("</think>", "</details>");
        renderMarkdown();
        return;
    }

    isDone = false;
    const chatNewMessage = JSON.parse(event.data);
    chat = chatNewMessage;
    answer.innerHTML = chat.messages.at(-1).content;
};

ws.onerror = function(error) {
    console.log("Ошибка " + error.message);
};

const onSend = () => {
    const textMessage = document.getElementById("message");
    const model = document.getElementById("model");
    const timer = document.getElementById("timer");

    if (textMessage != "") {
        model.disabled = true;
        chat.model = model.value;
        chat.messages.push({role: "user", content: textMessage.value});
        ws.send(JSON.stringify(chat));
        textMessage.value = "";
        timer.style.display = "block";
    }
}

const onRefresh = () => {
    chat = {model: document.getElementById("model").value, messages: []};
    isDone = true;
    const textMessage = document.getElementById("message");
    const model = document.getElementById("model");
    const answer = document.getElementById("answer");
    textMessage.value = "";
    model.disabled = false;
    answer.innerHTML = "";
}
