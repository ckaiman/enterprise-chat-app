function appendMessageToChat(message, sender) {
    const chatContainer = document.getElementById("chat-container");
    const messageElement = document.createElement("div");
    messageElement.textContent = message;
    if (sender === "bot") {
        messageElement.classList.add("bot-reply"); // For blue text styling
    }
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to the bottom
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
        const response = await fetch("http://localhost:8001/account/me", { // Directly call auth_service
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

function sendMessage() {
    let message = document.getElementById("chatbox").value;
    let token = localStorage.getItem("token");
    const chatbox = document.getElementById("chatbox");

    chatbox.value = ''; // Clear the input box immediately after getting the value

    fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({message})
    })
    .then(response => response.json())
    .then(data => {
        // Log to see what data.reply actually is
        console.log("Received data from /chat endpoint:", data);
        console.log("Type of data.reply:", typeof data.reply);
        console.log("Value of data.reply:", data.reply);
        let replyContent = data.reply;
        if (typeof replyContent === 'object' && replyContent !== null) {
            replyContent = JSON.stringify(replyContent, null, 2); // Pretty print JSON
        }
        // alert("Reply: " + replyContent); // Remove alert
        appendMessageToChat("You: " + message, "user"); // Display user's message
        appendMessageToChat("Bot: " + replyContent, "bot"); // Display bot's reply
    })
    .catch(error => console.error("Chat failed", error));
}