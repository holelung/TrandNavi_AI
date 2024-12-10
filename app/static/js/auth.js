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
            localStorage.setItem("user_name", data.user_name);
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
    window.location.href = "/start";
}

// cart
function click_cart() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/login";
        return;
    }

    window.location.href = "/cart";
}

// 로그아웃
function click_logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_name");
    window.location.href = "/";
}

// 회원가입
function sign_up() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
            email: email,
            password: password,
        }),
    })
        .then((response) => {
            if (response.ok) {
                alert("회원가입 완료");
                window.location.href = "/login";
                return;
            } else {
                throw new Error("회원가입에 실패했습니다.");
            }
        })
        .catch((error) => {
            console.error("회원가입 오류:", error);
            alert("동일한 계정이 존재합니다.");
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
