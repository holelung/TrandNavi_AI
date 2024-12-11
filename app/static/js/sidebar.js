// static/js/script.js
// 사이드바 로드 관련
console.log("JavaScript file is linked correctly!");

document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const closeSidebarButton = document.getElementById("close-sidebar-btn");
    const openSidebarButton = document.getElementById("open-sidebar-btn");

    console.log("채팅방 로드");
    loadChatRoomsOnLoad();

    // 창 크기에 따른 사이드바 상태 설정
    function handleSidebarVisibility() {
        if (window.innerWidth < 768) {
            sidebar.classList.add("hidden");
            openSidebarButton.classList.remove("hidden");
        } else {
            sidebar.classList.remove("hidden");
            openSidebarButton.classList.add("hidden");
        }
    }

    // 페이지 로드 시 사이드바 상태 설정
    sidebar.classList.add("hidden");
    openSidebarButton.classList.remove("hidden");

    // 창 크기가 변경될 때마다 사이드바 상태 변경
    window.addEventListener("resize", handleSidebarVisibility);

    // 사이드바 닫기
    closeSidebarButton.addEventListener("click", function () {
        sidebar.classList.add("hidden");
        openSidebarButton.classList.remove("hidden");
    });

    // 사이드바 열기
    openSidebarButton.addEventListener("click", function () {
        sidebar.classList.remove("hidden");
        openSidebarButton.classList.add("hidden");
    });
});

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
