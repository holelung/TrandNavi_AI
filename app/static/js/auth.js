// app/static/js/auth.js
function click_login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: email,
            password: password,
        }),
    })
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("로그인에 실패했습니다.");
            }
        })
        .then((data) => {
            // 로그인 성공 시 access_token을 저장
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            alert("로그인 성공!");

            loadChat();
        })
        .catch((error) => {
            console.error("로그인 오류:", error);
            alert("로그인에 실패했습니다. 이메일과 비밀번호를 확인하세요.");
        });
}

function loadChat() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/login";
        return;
    }

    // 토큰이 있을 때 바로 main 화면으로 이동
    window.location.href = "/main";
}
