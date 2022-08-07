let currentRecipient = "";
let chatInput = $("#chat-input");
let chatButton = $("#btn-send");
let userList = $("#user-list");
let messageList = $("#messages");
let chatDisplay = $("#chat-overlay");

function updateUserList() {
  $.getJSON("api/v1/user/", function (data) {
    userList.children(".user").remove();
    for (let i = 0; i < data.length; i++) {
      const userItem = `<a class="panel-block user">${data[i]["username"]}</a>`;
      $(userItem).appendTo("#user-list");
    }
    $(".user").click(function () {
      userList.children(".is-highlighted").removeClass("is-highlighted");
      let selected = event.target;
      $(selected).addClass("is-highlighted");
      setCurrentRecipient(selected.text);
      $("#chat-name").text(selected.text);
    });
  });
}

function drawMessage(message) {
  let position = "left";
  let belongsTo = "";
  const date = new Date(message.timestamp).toLocaleTimeString();
  if (message.user === currentUser) position = "right";
  if (message.user === currentUser) belongsTo = " me";
  const messageItem = `
            <li class="message ${position}">
                <div class="text_wrapper">
                    <div class="arrow-down${belongsTo}"></div>
                    <div class="text">${message.body}<br>
                        <span class="small">${date}</span>
                    </div>
                </div>
            </li>`;
  $(messageItem).appendTo("#messages");
}

function getConversation(recipient) {
  $.getJSON(`/api/v1/message/?target=${recipient}`, function (data) {
    messageList.children(".message").remove();
    for (let i = data["results"].length - 1; i >= 0; i--) {
      drawMessage(data["results"][i]);
    }
    messageList.animate({ scrollTop: messageList.prop("scrollHeight") });
  });
}

function getMessageById(message) {
  id = JSON.parse(message).message;
  $.getJSON(`/api/v1/message/${id}/`, function (data) {
    if (
      data.user === currentRecipient ||
      (data.recipient === currentRecipient && data.user == currentUser)
    ) {
      drawMessage(data);
    }
    messageList.animate({ scrollTop: messageList.prop("scrollHeight") });
  });
}

function sendMessage(recipient, body) {
  $.post("/api/v1/message/", {
    recipient: recipient,
    body: body,
  }).fail(function () {
    alert("Error! Check console!");
  });
}

function setCurrentRecipient(username) {
  currentRecipient = username;
  getConversation(currentRecipient);
  enableInput();
}

function enableInput() {
  chatInput.prop("disabled", false);
  chatButton.prop("disabled", false);
  chatInput.focus();
  chatDisplay.height("0px");
}

function disableInput() {
  chatInput.prop("disabled", true);
  chatButton.prop("disabled", true);
}

$(document).ready(function () {
  updateUserList();
  disableInput();

  //    let socket = new WebSocket(`ws://127.0.0.1:8000/?session_key=${sessionKey}`);
  var socket = new WebSocket(
    "ws://" + window.location.host + "/ws?session_key=${sessionKey}"
  );

  chatInput.keypress(function (e) {
    if (e.keyCode == 13) chatButton.click();
  });

  chatButton.click(function () {
    if (chatInput.val().length > 0) {
      sendMessage(currentRecipient, chatInput.val());
      chatInput.val("");
    }
  });

  socket.onmessage = function (e) {
    getMessageById(e.data);
  };
});
