// app/static/js/main.js
// main 로드시 실행되어야 할 함수들
document.addEventListener("DOMContentLoaded", function () {
    // 최근 채팅 기록 로드
    console.log("채팅 기록 로드");
    loadRecentChatHistory();
    console.log("채팅방 로드");
    loadChatRoomsOnLoad();
});

function loadRecentChatHistory() {
    // 최근 채팅방 ID를 설정 (예: 기본값 또는 로컬스토리지에서 로드)
    const recentRoomId = localStorage.getItem("room_id"); // 기본 채팅방 ID (적절히 수정)

    // Fetch API를 사용하여 채팅 기록 가져오기
    fetch(`/chat/${recentRoomId}/history`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`, // JWT 토큰 사용
        },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch chat history");
            }
            return response.json();
        })
        .then((data) => {
            renderChatHistory(data);
        })
        .catch((error) => {
            console.error("Error fetching chat history:", error);
        });
}

function renderChatHistory(messages) {
    const chatMessagesContainer = document.getElementById("chat-messages");

    messages.forEach((message) => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("mb-4");

        if (message.user_id === "BotMessage") {
            // Bot 메시지 스타일
            messageElement.innerHTML = `
                <div class="flex items-start">
                    <img src="${chatBotLogoUrl}" alt="Chatbot Logo" class="mr-2 w-12 h-12 rounded-full">
                    <div class="bg-gray-100 p-4 rounded-lg bot-message-content">
                        ${message.content}
                    </div>
                </div>
            `;
        } else {
            // User 메시지 스타일
            messageElement.innerHTML = `
                <div class="flex justify-end mb-4">
                    <div class="bg-blue-500 text-white p-4 rounded-lg">
                        ${message.content}
                    </div>
                </div>
            `;
        }

        chatMessagesContainer.appendChild(messageElement);
    });

    // 스크롤을 가장 아래로 이동
    chatMessagesContainer.scrollTop = chatMessagesContainer[0].scrollHeight;
}

function loadChatRoomsOnLoad() {
    fetch("/chat/rooms", {
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
    })
        .then((response) => response.json())
        .then((rooms) => {
            const chatRoomsContainer = $("#chat-rooms");
            chatRoomsContainer.empty();

            rooms.forEach((room) => {
                // 원래 형식에 맞게 변환필요
                chatRoomsContainer.append(`
                    <div class="chat-room-item" data-room-id="${room.room_id}">
                        <span>${room.room_name}</span>
                        <button class="delete-room-btn" data-room-id="${room.room_id}">삭제</button>
                    </div>
                `);
            });

            // 채팅방 클릭 이벤트 추가
            $(".chat-room-item").click(function () {
                const roomId = $(this).data("room-id");
                loadChatHistory(roomId);
            });

            // 삭제 버튼 클릭 이벤트 추가
            $(".delete-room-btn").click(function (e) {
                e.stopPropagation();
                const roomId = $(this).data("room-id");
                deleteChatRoom(roomId);
            });
        })
        .catch((error) => {
            console.error("Error loading chat rooms:", error);
            alert("채팅방 목록 로드 중 오류가 발생했습니다.");
        });
}
