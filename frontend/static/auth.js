function login() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    fetch("/auth/login", {
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

function updateLoginLogoutButton() {
    const button = document.getElementById("login-logout-button");
    if (!button) return; // Safety check if button doesn't exist

    const token = localStorage.getItem("token");

    if (token) {
        button.textContent = "Logout";
        button.onclick = function() {
            localStorage.removeItem("token");
            window.location.href = "login.html";
        };
    } else {
        // This state should ideally not be reached on index.html due to the redirect logic,
        // but it's good practice for the function to handle it.
        button.textContent = "Login";
        button.onclick = function() {
            window.location.href = "login.html";
        };
    }
}

async function loadUserDetailsAndWelcome() {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
        const response = await fetch("/account/me", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });
        if (response.ok) {
            const userData = await response.json();
            const fullName = userData.name || "User";
            const firstName = fullName.split(" ")[0]; // Get the first name
            document.getElementById("welcome-header").textContent = `Welcome, ${firstName}, to the Chat Assistant`;
        } else {
            console.error("Failed to fetch user details:", response.status);
        }
    } catch (error) {
        console.error("Error fetching user details:", error);
    }
    // Always update the button state after attempting to load user details
    updateLoginLogoutButton();
}