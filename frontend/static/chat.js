function showToast(message) {
    const toast = document.getElementById("toast-notification");
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");

    // After 3 seconds, remove the show class
    setTimeout(() => { toast.classList.remove("show"); }, 3000);
}

// This will hold the state of the conversation if the bot needs to ask a clarifying question.
let conversationContext = null;

function appendTurnToChat(userMessage, botMessage, botData = null) {
    const chatContainer = document.getElementById("chat-container");
    
    // Create a container for the whole turn to group user and bot messages.
    const turnElement = document.createElement("div");
    turnElement.classList.add("chat-turn");

    // 1. Create and add the user message element
    const userMessageElement = document.createElement("div");
    const userPrefix = document.createElement("strong");
    // Get first name of the user from the token
    const token = localStorage.getItem("token"); // It's safe to assume token exists here, as we check on page load.
    const decodedToken = JSON.parse(atob(token.split('.')[1])); // Decode the payload of the JWT
    const userFullName = decodedToken.name || "User"; // Get the full name from the token, fallback to "User"
    const userFirstName = userFullName.split(" ")[0]; // Extract the first name
    userPrefix.textContent = `${userFirstName}: `;
    userMessageElement.appendChild(userPrefix);
    userMessageElement.appendChild(document.createTextNode(userMessage));
    turnElement.appendChild(userMessageElement);

    // 2. Create and add the bot message element
    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("bot-reply");
    let botMessageHTML = "<strong>SAAssistant:</strong> " + botMessage;
    if (botData && typeof botData === 'object' && Object.keys(botData).length > 0) {
        const jsonDataString = JSON.stringify(botData, null, 2);
        botMessageHTML += `
            <div class="result-box">
                <pre class="json-response">${jsonDataString}</pre>
            </div>`;
    }
    botMessageElement.innerHTML = botMessageHTML;
    turnElement.appendChild(botMessageElement);

    // 3. Prepend the whole turn to the main chat container
    // Change from prepend to append to have the latest message at the bottom.
    chatContainer.appendChild(turnElement);
    // Scroll to the bottom of the chat container to show the new message.
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    let message = document.getElementById("chatbox").value;
    let token = localStorage.getItem("token");
    const chatbox = document.getElementById("chatbox");

    if (!message.trim()) return; // Don't send empty messages

    chatbox.value = ''; // Clear the input box immediately

    // Prepare the payload, including any existing conversation context
    const payload = {
        message: message
    };
    if (conversationContext) {
        payload.context = conversationContext;
    }

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        let replyContent = data.reply;
        let dataPayload = data.data; // Get the raw data payload

        // Handle the context for the next turn. If the backend sends a context
        // object, we store it. Otherwise, we clear it.
        if (data.context) {
            conversationContext = data.context;
        } else {
            conversationContext = null;
        }

        if (replyContent === undefined || replyContent === null) {
            replyContent = "I'm sorry, I encountered an issue and can't provide a response right now.";
        }

        appendTurnToChat(message, replyContent, dataPayload);
    })
    .catch(error => {
        console.error("Chat failed", error);
        conversationContext = null; // Clear context on network error
    });
}

// Add event listener for Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    // Check for authentication token. If not present, redirect to the login page.
    if (!localStorage.getItem("token")) {
        window.location.href = "login.html";
        return; // Stop further script execution
    } else {
        // If authenticated, load user details and set up the logout button.
        // This function is defined in auth.js
        loadUserDetailsAndWelcome();
    }

    const chatbox = document.getElementById('chatbox');
    if (chatbox) {
        chatbox.addEventListener('keydown', function(event) {
            // Send message on Enter key press, but allow new lines with Shift+Enter
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault(); // Prevents adding a new line
                sendMessage();
            }
        });
    }
});
