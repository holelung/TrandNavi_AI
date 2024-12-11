// app/static/js/start.js

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
function createChatRoom(roomName) {
    fetch("/chat/createRoom", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ room_name: roomName }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("[DEBUG] 서버 응답:", data);
            if (data.room_id) {
                console.log(`채팅방 '${data.room_name}'이(가) 생성되었습니다.`);
                // 방 아이디를 localStorage에 저장
                localStorage.setItem("room_id", data.room_id);

                fetch(`/main/id:${localStorage.getItem("room_id")}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${localStorage.getItem(
                            "access_token"
                        )}`,
                    },
                    body: JSON.stringify({ room_name: roomName }),
                })
                    .then((response) => {
                        console.log(
                            "[DEBUG] /main/id:<room_id> 응답 상태:",
                            response.status
                        );
                        if (response.redirected) {
                            console.log(
                                "[DEBUG] 리다이렉션 URL:",
                                response.url
                            );
                            // 서버에서 리다이렉션이 발생한 경우, 리다이렉션된 URL로 이동
                            window.location.href = response.url;
                        } else {
                            console.error("[DEBUG] 리다이렉션 실패:", response);
                            alert(
                                "채팅방으로 이동하는 중 오류가 발생했습니다."
                            );
                        }
                    })
                    .catch((error) => {
                        console.error("Error redirecting to chat room:", error);
                    });

                // window.location.href = `/main/id:${localStorage.getItem(
                //     "room_id"
                // )}`;
            } else {
                console.error("[DEBUG] room_id가 없음:", data);
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
