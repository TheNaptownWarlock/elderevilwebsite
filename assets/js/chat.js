// Initialize Socket.IO connection
const socket = io();

// DOM Elements
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chatDisplay = document.getElementById('chat-display');
const usernameModal = document.getElementById('username-modal');
const usernameForm = document.getElementById('username-form');
const usernameInput = document.getElementById('username-input');
const currentUsername = document.getElementById('current-username');

// Check if username exists in localStorage
let username = localStorage.getItem('username');
if (!username) {
    usernameModal.style.display = 'block';
} else {
    currentUsername.textContent = username;
    if (username === 'TheNaptownWarlock') {
        currentUsername.classList.add('special-username');
    }
}

// Handle username submission
usernameForm.addEventListener('submit', (e) => {
    e.preventDefault();
    username = usernameInput.value.trim();
    if (username) {
        if (username === 'TheNaptownWarlock') {
            // Check if this is the actual Naptown Warlock
            const isAuthorized = confirm('Are you the actual Naptown Warlock?');
            if (!isAuthorized) {
                alert('Sorry, only the actual Naptown Warlock can use this username.');
                return;
            }
        }
        localStorage.setItem('username', username);
        currentUsername.textContent = username;
        if (username === 'TheNaptownWarlock') {
            currentUsername.classList.add('special-username');
        }
        usernameModal.style.display = 'none';
        appendMessage('System', `Welcome to the chat, ${username}!`, new Date());
    }
});

// Handle chat form submission
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message && username) {
        socket.emit('chat message', {
            text: message,
            user: username
        });
        messageInput.value = '';
    }
});

// Handle incoming messages
socket.on('chat message', (msg) => {
    appendMessage(msg.user, msg.text, new Date(msg.timestamp));
});

// Handle previous messages
socket.on('previous messages', (msgs) => {
    msgs.forEach(msg => {
        appendMessage(msg.user, msg.text, new Date(msg.timestamp));
    });
});

// Function to append messages to the chat display
function appendMessage(user, text, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const timeString = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userSpan = document.createElement('span');
    userSpan.className = 'message-user';
    if (user === 'TheNaptownWarlock') {
        userSpan.classList.add('special-username');
    }
    userSpan.textContent = user + ':';
    
    messageDiv.appendChild(userSpan);
    messageDiv.appendChild(document.createTextNode(' ' + text));
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = timeString;
    messageDiv.appendChild(timeSpan);
    
    chatDisplay.appendChild(messageDiv);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

// Add some initial styling
const style = document.createElement('style');
style.textContent = `
    .message {
        margin: 10px 0;
        padding: 8px;
        background: #f0f0f0;
        border-radius: 4px;
    }
    .message-user {
        font-weight: bold;
        color: #333;
    }
    .special-username {
        color: #8a2be2; /* Purple color for TheNaptownWarlock */
        text-shadow: 0 0 5px rgba(138, 43, 226, 0.3);
    }
    .message-time {
        float: right;
        color: #666;
        font-size: 0.8em;
    }
    #username-modal {
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    #current-username {
        font-weight: bold;
        color: #333;
    }
`;
document.head.appendChild(style); 