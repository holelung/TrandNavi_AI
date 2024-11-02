// app/static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
    const profileMenu = document.getElementById("profileMenu");
    profileMenu.classList.toggle("hidden");
});
function toggleMenu() {
    const menu = document.getElementById("profileMenu");
    menu.classList.toggle("hidden");
}
