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
    const userIcon = document.getElementById("user-profile-icon");

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
        if (userIcon) userIcon.style.display = 'none'; // Hide icon if not logged in
    }
}

async function loadUserDetailsAndWelcome() {
    const token = localStorage.getItem("token");
    if (!token) {
        // This case is already handled on the chat page, but this is a good safeguard.
        window.location.href = "login.html";
        return;
    }

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
            document.getElementById("welcome-header").textContent = `Welcome, ${firstName}, to the SAAssistant`;

            // --- Profile Icon & Modal Logic ---
            const userIcon = document.getElementById("user-profile-icon");
            const modal = document.getElementById("user-profile-modal");
            const closeBtn = document.querySelector(".close-button");

            if (userIcon) {
                userIcon.style.display = 'block';
            }

            // Populate modal with user data
            document.getElementById("modal-user-name").textContent = userData.name || 'N/A';
            document.getElementById("modal-user-role").textContent = userData.role || 'N/A';
            document.getElementById("modal-user-office").textContent = userData.office ? userData.office.name : 'N/A';

            // Add event listeners to open/close the modal
            if (userIcon && modal && closeBtn) {
                userIcon.onclick = () => { modal.style.display = "block"; };
                closeBtn.onclick = () => { modal.style.display = "none"; };
                // When the user clicks anywhere outside of the modal, close it
                window.onclick = (event) => {
                    if (event.target == modal) {
                        modal.style.display = "none";
                    }
                };
            }
        } else {
            // If the token is invalid or expired, the API will return an error (e.g., 401).
            // We should clear the bad token and redirect to the login page.
            console.error("Failed to fetch user details:", response.status);
            localStorage.removeItem("token");
            window.location.href = "login.html";
            return; // Stop further execution
        }
    } catch (error) {
        console.error("Error fetching user details:", error);
    }
    // Always update the button state after attempting to load user details
    updateLoginLogoutButton();
}