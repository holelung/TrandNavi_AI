console.log("chat.js connection");
// 채팅창 챗봇 로고
const chatbotLogoUrl = $("#chat-messages").data("chatbot-logo");

// 페이지 로드 시 초기 메시지 추가
$(document).ready(function () {
    const initialMessage =
        "안녕하세요 쇼핑몰 비서 AI서비스 트렌드 네비게이터 입니다.";
    addBotMessage(initialMessage);
});

// bot chat생성
function addBotMessage(message) {
    const markedMessage = marked.parse(message);
    const sanitizedMessage = DOMPurify.sanitize(markedMessage);
    $("#chat-messages").append(
        `<div class="flex items-start mb-4">
            <img src="${chatbotLogoUrl}" alt="Chatbot Logo" class="mr-2 w-12 h-12 rounded-full">
            <div class="bg-gray-100 p-4 rounded-lg bot-message-content">
                ${sanitizedMessage}
            </div>
        </div>`
    );
    // 스크롤 위치를 맨아래로 이동
    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
}

// user chat 생성
function sendMessage() {
    var userMessage = $("#user-input").val();
    if (userMessage.trim() === "") return;

    $("#chat-messages").append(
        `<div class="flex justify-end mb-4">
            <div class="bg-blue-500 text-white p-4 rounded-lg">
                ${userMessage}
            </div>
        </div>`
    );
    $("#user-input").val("");
    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);

    var botMessageContainer = $(
        `<div class="flex items-start mb-4">
            <img src="${chatbotLogoUrl}" alt="Chatbot Logo" class="mr-2 w-12 h-12 rounded-full">
            <div class="bg-gray-100 p-4 rounded-lg bot-message-content">
            </div>
        </div>`
    );
    $("#chat-messages").append(botMessageContainer);

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
    }).then((response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log("Stream complete");
                    return;
                }
                const chunk = decoder.decode(value);
                const lines = chunk.split("\n");
                lines.forEach((line) => {
                    if (line.startsWith("data: ")) {
                        const data = JSON.parse(line.slice(6));
                        const markedResponse = marked.parse(data.response);
                        console.log("파싱 결과: ", markedResponse);
                        const sanitizedResponse =
                            DOMPurify.sanitize(markedResponse);
                        // botMessageContainer의 특정 div에 응답 메시지 추가
                        botMessageContainer
                            .find(".bot-message-content")
                            .html(sanitizedResponse);
                        $("#chat-messages").scrollTop(
                            $("#chat-messages")[0].scrollHeight
                        );
                    }
                });
                readStream();
            });
        }

        readStream();
    });
}

$("#send-button").click(sendMessage);

$("#user-input").keypress(function (e) {
    if (e.which == 13) {
        sendMessage();
        return false;
    }
});
