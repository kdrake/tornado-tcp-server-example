$(function () {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function () {
    };

    MessageHandler.start();
    SourceHandler.start();
});

var MessageHandler = {
    socket: null,

    start: function () {
        var url = "ws://" + location.host + "/m-ws";
        MessageHandler.socket = new WebSocket(url);
        MessageHandler.socket.onmessage = function (event) {
            MessageHandler.showMessage(JSON.parse(event.data));
        }
    },
    showMessage: function (message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;

        var node = $(message.html);
        node.hide();

        $("#message-list").append(node);
        node.slideDown();
    }
};

var SourceHandler = {
    socket: null,

    start: function () {
        var url = "ws://" + location.host + "/s-ws";
        SourceHandler.socket = new WebSocket(url);
        SourceHandler.socket.onmessage = function (event) {
            SourceHandler.sync(JSON.parse(event.data));
        }
    },
    sync: function (data) {
        $("#source-list").html(data.html);
    }
};
