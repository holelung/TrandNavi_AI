// app/static/js/start.js
document.addEventListener("DOMContentLoaded", function () {
    console.log("채팅방 로드");
    loadChatRoomsOnLoad();
});

$(document).ready(function () {
    $("#start-send-button").click(function (e) {
        e.preventDefault();

        const roomName = $("#start-user-input").val().trim();
        if (roomName === "") {
            alert("질문을 입력해주세요.");
            return;
        }
        createChatRoom(roomName);
    });
});

// 유저 ID 호출 함수
function getCurrentUserId() {
    const payload = JSON.parse(
        atob(localStorage.getItem("access_token").split(".")[1])
    );
    return payload.sub; // JWT payload에서 사용자 ID(sub)를 가져옴
}

// 채팅방 생성 함수
async function createChatRoom(roomName) {
    fetch("/chat/createRoom", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ room_name: roomName }),
    })
        .then((response) => response.json())
        .then(async (data) => {
            if (data.room_id) {
                console.log(`채팅방 '${data.room_name}'이(가) 생성되었습니다.`);
                // 방 아이디를 localStorage에 저장
                localStorage.setItem("room_id", data.room_id);
                console.log("사용자 입력저장");
                await saveMessageToRoom(data.room_id, data.room_name);
                console.log("llm 답변생성");
                await sendMessageFromStart(data.room_id, data.room_name);

                // 작업이 완료된 후 이동
                window.location.href = "/main";
            } else {
                alert("채팅방 생성에 실패했습니다.");
            }
        })
        .catch((error) => {
            console.error("Error creating chat room:", error);
            alert("채팅방 생성 중 오류가 발생했습니다.");
        });
}

async function sendMessageFromStart(room_id, room_name) {
    fetch("/chat/createMessage", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: room_name, room_id: room_id }),
    }).then((response) => {
        if (response.status === 401) {
            return refreshAccessToken().then((refreshSuccess) => {
                if (refreshSuccess) {
                    return sendMessageFromStart(room_id, room_name);
                } else {
                    alert("로그인이 필요합니다.");
                    return null;
                }
            });
        } else {
            console.log("Message생성");
        }
        localStorage.setItem("room_id", room_id);
    });
}

async function saveMessageToRoom(room_id, room_name) {
    fetch(`/chat/${room_id}/message`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: room_name, room_id: room_id }),
    })
        .then((response) => {
            if (response.ok) {
                console.log("message save success!");
            } else {
                console.log("저장실패");
            }
        })
        .catch((error) => {
            console.error("Error creating save message: ", error);
            alert("오류발생");
        });
}

function loadChatRoomsOnLoad() {
    fetch("/chat/rooms", {
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
    })
        .then((response) => response.json())
        .then((rooms) => {
            if (!rooms) {
                throw err;
            } else {
                const chatRoomsContainer = $("#chat-rooms");
                chatRoomsContainer.empty();

                rooms.forEach((room) => {
                    // 원래 형식에 맞게 변환필요
                    chatRoomsContainer.append(`
                    <div class="chat-room-item flex justify-between items-center p-2 hover:bg-gray-600 rounded-lg" data-room-id="${room.room_id}" data-room-name="${room.room_name}>
                        <span class="text-sm text-ellipsis overflow-hidden whitespace-nowrap">
                            ${room.room_name}
                        </span>
                        <button class="delete-room-btn bg-red-500 text-white rounded px-2 py-1 text-xs" data-room-id="${room.room_id}">
                            삭제
                        </button>
                    </div>
                `);
                });
            }

            // 채팅방 클릭 이벤트 추가
            $(".chat-room-item").click(function () {
                const roomId = $(this).data("room-id");
                window.location.href = `/main/id:${roomId}`;
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

// 채팅 기록 불러오기
function loadChatHistory(roomId) {
    fetch(`/chat/${roomId}/history`, {
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
    })
        .then((response) => response.json())
        .then((messages) => {
            const chatMessagesContainer = $("#chat-messages");
            chatMessagesContainer.empty();

            messages.forEach((msg) => {
                const messageHtml = `
                    <div class="${
                        msg.user_id === getCurrentUserId()
                            ? "flex justify-end mb-4"
                            : "flex items-start mb-4"
                    }">
                        <div class="${
                            msg.user_id === getCurrentUserId()
                                ? "bg-blue-500 text-white"
                                : "bg-gray-100"
                        } p-4 rounded-lg">
                            ${msg.content}
                        </div>
                    </div>
                `;
                chatMessagesContainer.append(messageHtml);
            });

            chatMessagesContainer.scrollTop =
                chatMessagesContainer.scrollHeight; // [0] 제거
        })
        .catch((error) => {
            console.error("Error loading chat history:", error);
            alert("채팅 기록 로드 중 오류가 발생했습니다.");
        });
}
