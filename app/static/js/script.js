// app/static/js/script.js
// document.addEventListener("DOMContentLoaded", function () {
//     const profileMenu = document.getElementById("profileMenu");
//     profileMenu.classList.toggle("hidden");
// });

// function toggleMenu() {
//     const menu = document.getElementById("profileMenu");
//     menu.classList.toggle("hidden");
// }
// 메뉴 열기 및 닫기 상태 관리
function toggleMenu() {
    const menu = document.getElementById("profileMenu");
    menu.classList.toggle("hidden");
}

// 외부 클릭 감지하여 메뉴 닫기
document.addEventListener("click", function (event) {
    const menu = document.getElementById("profileMenu");
    const button = document.querySelector("[data-testid='profile-button']");

    // 메뉴와 버튼 영역 외부를 클릭했는지 확인
    if (
        menu &&
        !menu.classList.contains("hidden") &&
        !menu.contains(event.target) &&
        !button.contains(event.target)
    ) {
        menu.classList.add("hidden");
    }
});

// 장바구니 연결
async function addToCart(productName, price, productImg, brand) {
    const response = await fetch("/cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("jwt_token")}`, // JWT 토큰이 필요할 경우
        },
        body: JSON.stringify({
            product_name: productName,
            price: price,
            product_img: productImg,
            product_detail: brand,
        }),
    });

    const result = await response.json();
    if (response.ok) {
        alert(result.message); // "Item add to cart" 메시지 표시
    } else {
        alert(result.error || "Failed to add item to cart");
    }
}
