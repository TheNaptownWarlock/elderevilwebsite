// Chat functionality
const chatForm = document.getElementById('chat-form');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');

// Store messages in memory
let messages = [];

// Handle form submission
chatForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent form from submitting and page reload
    const message = messageInput.value.trim();
    if (message) {
        // Add message to the array
        messages.push({
            text: message,
            timestamp: new Date(),
            user: 'TheNaptownWarlock'
        });
        
        // Update the chat display
        updateChatDisplay();
        
        // Clear the input
        messageInput.value = '';
    }
});

// Update the chat display
function updateChatDisplay() {
    chatMessages.innerHTML = '';
    messages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `
            <span class="message-user">${message.user}:</span>
            <span class="message-text">${message.text}</span>
            <span class="message-time">${message.timestamp.toLocaleTimeString()}</span>
        `;
        chatMessages.appendChild(messageElement);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add some initial messages
messages.push(
    {
        text: "Welcome to the chat! Feel free to ask me anything about my projects or creative process.",
        timestamp: new Date(),
        user: 'TheNaptownWarlock'
    },
    {
        text: "I'm currently working on some new ice cream flavors and clay creations. What would you like to know about?",
        timestamp: new Date(),
        user: 'TheNaptownWarlock'
    }
);

// Display initial messages
updateChatDisplay(); 