// app/static/js/main.js
// main 로드시 실행되어야 할 함수들
document.addEventListener("DOMContentLoaded", function () {
    // 최근 채팅 기록 로드
    console.log("채팅 기록 로드");
    loadRecentChatHistory();
});

function getCurrentUserId() {
    const payload = JSON.parse(
        atob(localStorage.getItem("access_token").split(".")[1])
    );
    return payload.sub; // JWT payload에서 사용자 ID(sub)를 가져옴
}

function loadRecentChatHistory() {
    // 최근 채팅방 ID를 설정 (예: 기본값 또는 로컬스토리지에서 로드)
    const recentRoomId = localStorage.getItem("room_id"); // 기본 채팅방 ID (적절히 수정)
    window.location.href = `/main/id:${recentRoomId}`;
}
