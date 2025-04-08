// Initialize Firebase
const firebaseConfig = {
    // You'll need to add your Firebase config here
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Chat functionality
const chatForm = document.getElementById('chat-form');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        db.collection('messages').add({
            text: message,
            timestamp: firebase.firestore.FieldValue.serverTimestamp(),
            user: 'TheNaptownWarlock' // You can make this dynamic later
        });
        messageInput.value = '';
    }
});

// Listen for new messages
db.collection('messages')
    .orderBy('timestamp')
    .onSnapshot((snapshot) => {
        chatMessages.innerHTML = '';
        snapshot.forEach((doc) => {
            const message = doc.data();
            const messageElement = document.createElement('div');
            messageElement.className = 'message';
            messageElement.innerHTML = `
                <span class="message-user">${message.user}:</span>
                <span class="message-text">${message.text}</span>
                <span class="message-time">${new Date(message.timestamp?.toDate()).toLocaleTimeString()}</span>
            `;
            chatMessages.appendChild(messageElement);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }); 