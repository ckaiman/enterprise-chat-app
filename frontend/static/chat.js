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

    // --- Chat Widget Toggle Logic ---
    const chatLauncher = document.getElementById('chat-launcher');
    const chatWidget = document.getElementById('chat-widget');
    const closeChatWidget = document.getElementById('close-chat-widget');
    // Get the new expand/contract buttons
    const expandBtn = document.getElementById('expand-widget-btn');
    const contractBtn = document.getElementById('contract-widget-btn');

    if (chatLauncher && chatWidget && closeChatWidget) {
        chatLauncher.onclick = () => {
            chatWidget.style.display = 'flex'; // Use flex to enable column layout
            chatLauncher.style.display = 'none';
        };
        closeChatWidget.onclick = () => {
            chatWidget.style.display = 'none';
            chatLauncher.style.display = 'block';
        };
    }

    // --- Chat Widget Resize Logic ---
    if (chatWidget && expandBtn && contractBtn) {
        expandBtn.onclick = () => {
            chatWidget.classList.add('expanded');
        };
        contractBtn.onclick = () => {
            chatWidget.classList.remove('expanded');
        };
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

        // --- Speech Recognition ---
        const micToggle = document.getElementById('mic-toggle');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition && micToggle) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true; // Keep listening until stopped
            recognition.interimResults = true; // Show results as they are recognized
            recognition.lang = 'en-US'; // Explicitly set to the most widely supported language as a final attempt.

            micToggle.addEventListener('change', () => {
                if (micToggle.checked) {
                    try {
                        chatbox.placeholder = "Listening...";
                        chatbox.value = ""; // Clear any error messages
                        chatbox.style.color = 'inherit';
                        recognition.start();
                    } catch(e) {
                        console.error("Speech recognition could not be started.", e);
                        chatbox.value = "Error: Recognition already active.";
                        chatbox.style.color = 'red';
                        micToggle.checked = false;
                    }
                } else {
                    chatbox.placeholder = "Enter your request or question...";
                    recognition.stop();
                }
            });

            recognition.onresult = (event) => {
                let interim_transcript = '';
                let final_transcript = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final_transcript += event.results[i][0].transcript;
                    } else {
                        interim_transcript += event.results[i][0].transcript;
                    }
                }
                chatbox.value = final_transcript + interim_transcript;
            };

            recognition.onerror = (event) => {
                console.error("Speech recognition error:", event.error);
                let errorMessage = `Speech Error: ${event.error}`;

                // Provide a more helpful message and permanently disable the feature if language is not supported.
                if (event.error === 'language-not-supported') {
                    errorMessage = "Voice input is not supported by your browser. This feature will now be hidden.";
                    // Permanently hide the toggle switch as it's not supported.
                    micToggle.parentElement.style.display = 'none';
                }

                showToast(errorMessage);
                micToggle.checked = false; // Turn off toggle on error
            };

            recognition.onend = () => {
                micToggle.checked = false; // Ensure toggle is off when recognition ends
                chatbox.placeholder = "Enter your request or question...";
            };
        }
    }
});
