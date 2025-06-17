function login() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    fetch("http://localhost:8001/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    })
    .then(response => response.json())
    .then(data => {
        localStorage.setItem("token", data.access_token);
        window.location.href = "index.html";  // Redirect to chat UI after login
    })
    .catch(error => console.error("Login failed", error));
}