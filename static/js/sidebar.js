// static/js/script.js

console.log("JavaScript file is linked correctly!");

document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const closeSidebarButton = document.getElementById("close-sidebar-btn");
    const openSidebarButton = document.getElementById("open-sidebar-btn");

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
    handleSidebarVisibility();

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
