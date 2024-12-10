console.log("chat.js connection");

// 유저 ID 호출 함수
function getCurrentUserId() {
    const payload = JSON.parse(
        atob(localStorage.getItem("access_token").split(".")[1])
    );
    return payload.sub; // JWT payload에서 사용자 ID(sub)를 가져옴
}

// 채팅창 챗봇 로고
const chatbotLogoUrl = $("#chat-messages").data("trendNavi-logo");

// 페이지 로드 시 초기 메시지 추가
$(document).ready(function () {
    const initialMessage =
        "안녕하세요 쇼핑몰 비서 AI서비스 트렌드 네비게이터 입니다.";
    addBotMessage(initialMessage);

    // 파일 선택 버튼 클릭 시 파일 선택 창 열기
    $("#upload-btn").click(function () {
        $("#image-input").click(); // 파일 선택 창을 열기
    });

    // 파일 선택 후 업로드 시작
    $("#image-input").change(function () {
        uploadImage(); // 이미지 업로드 함수 호출
    });
});

// bot chat 생성
function addBotMessage(message) {
    const sanitizedMessage = DOMPurify.sanitize(message);

    // LLM 응답을 그대로 출력
    $("#chat-messages").append(
        `<div class="flex items-start mb-4">
            <img src="${chatBotLogoUrl}" alt="Chatbot-Logo" class="mr-2 w-12 h-12 rounded-full">
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
    const token = localStorage.getItem("access_token");

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
            <div class="bg-gray-100 p-4 rounded-lg bot-message-content"></div>
        </div>`
    );
    $("#chat-messages").append(botMessageContainer);

    fetch("/chat/createMessage", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
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

                    // add-to-cart 버튼에 이벤트 리스너 추가
                    botMessageContainer
                        .find('[data-action="add-to-cart"]')
                        .each(function () {
                            const productName = $(this).data("product-name");
                            const price = $(this).data("price");
                            const productImg = $(this).data("product-img");
                            const brand = $(this).data("brand");
                            const productUrl = $(this).data("product-url");

                            $(this)
                                .off("click")
                                .on("click", function () {
                                    addToCart(
                                        productName,
                                        price,
                                        productImg,
                                        brand,
                                        productUrl
                                    );
                                });
                        });
                    return;
                }

                const chunk = decoder.decode(value);

                const lines = chunk.split("\n");
                lines.forEach((line) => {
                    if (line.startsWith("data: ")) {
                        const jsonString = line.slice(6).trim(); // 앞뒤 공백 제거
                        try {
                            const data = JSON.parse(jsonString); // JSON 파싱
                            const sanitizedResponse = DOMPurify.sanitize(
                                data.response,
                                {
                                    ALLOWED_TAGS: [
                                        "img",
                                        "a",
                                        "div",
                                        "span",
                                        "li",
                                        "button",
                                        "br",
                                        "pre",
                                    ],
                                    ALLOWED_ATTR: [
                                        "src",
                                        "href",
                                        "alt",
                                        "class",
                                        "id",
                                    ],
                                }
                            );
                            botMessageContainer
                                .find(".bot-message-content")
                                .html(sanitizedResponse);
                            $("#chat-messages").scrollTop(
                                $("#chat-messages")[0].scrollHeight
                            );
                        } catch (error) {
                            console.error("JSON 파싱 실패:", error, jsonString);
                        }
                    }
                });
                readStream();
            });
        }

        readStream();
    });
}

// 이미지 업로드 후 메시지를 보내는 함수
function uploadImage() {
    var fileInput = $("#image-input")[0].files[0];
    if (!fileInput) {
        console.log("파일이 선택되지 않았습니다.");
        return;
    }

    var formData = new FormData();
    formData.append("file", fileInput);

    $("#chat-messages").append(
        `<div class="flex justify-end mb-4">
            <div class="bg-blue-500 text-white p-4 rounded-lg">
                이미지를 업로드 중입니다...
            </div>
        </div>`
    );
    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);

    var botMessageContainer = $(
        `<div class="flex items-start mb-4">
            <img src="${chatbotLogoUrl}" alt="Chatbot Logo" class="mr-2 w-12 h-12 rounded-full">
            <div class="bg-gray-100 p-4 rounded-lg bot-message-content"></div>
        </div>`
    );
    $("#chat-messages").append(botMessageContainer);

    fetch("/upload", {
        method: "POST",
        body: formData,
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
                        const sanitizedResponse = DOMPurify.sanitize(
                            data.response
                        );

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

$("#send-button").click(function (e) {
    e.preventDefault();
    sendMessage();
});

$("#user-input").keypress(function (e) {
    if (e.which == 13) {
        e.preventDefault();
        sendMessage();
        return false;
    }
});

// 카트에 아이템 추가
function addToCart(productName, price, productImg, brand, productUrl) {
    console.log("Adding to cart:", {
        product_name: productName,
        price: price,
        product_img: productImg,
        product_detail: brand,
        product_url: productUrl,
    });

    fetch("/cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
            product_name: productName,
            price: price,
            product_img: productImg,
            product_detail: brand,
            product_url: productUrl,
        }),
    })
        .then((response) => {
            if (response.status === 401) {
                return refreshAccessToken().then((refreshSuccess) => {
                    if (refreshSuccess) {
                        return addToCart(
                            productName,
                            price,
                            productImg,
                            brand,
                            productUrl
                        );
                    } else {
                        alert("로그인이 필요합니다.");
                        return null;
                    }
                });
            }

            console.log("Response status:", response.status);
            console.log("Response headers:", [...response.headers.entries()]);

            if (!response.ok) {
                alert(`HTTP error! Status: ${response.status}`);
                return;
            }

            return response.json().then((result) => {
                console.log("Response data:", result);
                alert(result.message || "Item added to cart");
            });
        })
        .catch((error) => {
            console.error("Error adding to cart:", error);
            alert("Failed to add item to cart.");
        });
}

// 채팅방 생성 버튼 클릭 이벤트
$("#create-room-button").click(function () {
    //
    const roomName = prompt("채팅방 이름을 입력하세요:");
    if (roomName) {
        createChatRoom(roomName);
    }
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
                alert(`채팅방 '${data.room_name}'이(가) 생성되었습니다.`);
                loadChatRooms(); // 새로고침
            } else {
                alert("채팅방 생성에 실패했습니다.");
            }
        })
        .catch((error) => {
            console.error("Error creating chat room:", error);
            alert("채팅방 생성 중 오류가 발생했습니다.");
        });
}

// 채팅방 목록 로드
function loadChatRooms() {
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

// 채팅방 삭제
function deleteChatRoom(roomId) {
    if (!confirm("정말 이 채팅방을 삭제하시겠습니까?")) return;

    fetch(`/chat/${roomId}`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message || "채팅방이 삭제되었습니다.");
            loadChatRooms(); // 채팅방 목록 갱신
        })
        .catch((error) => {
            console.error("Error deleting chat room:", error);
            alert("채팅방 삭제 중 오류가 발생했습니다.");
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

            chatMessagesContainer.scrollTop(
                chatMessagesContainer[0].scrollHeight
            );
        })
        .catch((error) => {
            console.error("Error loading chat history:", error);
            alert("채팅 기록 로드 중 오류가 발생했습니다.");
        });
}

// 액새스 토큰 갱신
async function refreshAccessToken() {
    try {
        const response = await fetch("/refresh", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${localStorage.getItem(
                    "refresh_token"
                )}`,
            },
        });

        if (response.ok) {
            const tokens = await response.json();
            accessToken = tokens.access_token;
            refreshToken = tokens.refresh_token || refreshToken;

            // 새 토큰을 로컬 스토리지에 저장
            localStorage.setItem("access_token", accessToken);
            localStorage.setItem("refresh_token", refreshToken);

            return true;
        } else {
            const errorMsg = await response.text();
            console.error("리프레시 실패:", response.status, errorMsg);
            return false;
        }
    } catch (error) {
        console.error("네트워크 오류:", error);
        return false;
    }
}
