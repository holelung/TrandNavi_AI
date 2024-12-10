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
            if (data.room_id) {
                console.log(`채팅방 '${data.room_name}'이(가) 생성되었습니다.`);
                // 방 아이디를 localStorage에 저장
                // localStorage.setItem("current_room_id", data.room_id);
                console.log("사용자 입력저장");
                saveMessageToRoom(data.room_id, data.room_name);
                console.log("llm 답변생성");
                sendMessageFromStart(data.room_id, data.room_name);
            } else {
                alert("채팅방 생성에 실패했습니다.");
            }
            window.location.href = "/main";
        })
        .catch((error) => {
            console.error("Error creating chat room:", error);
            alert("채팅방 생성 중 오류가 발생했습니다.");
        });
}

function sendMessageFromStart(room_id, room_name) {
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

function saveMessageToRoom(room_id, room_name) {
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
