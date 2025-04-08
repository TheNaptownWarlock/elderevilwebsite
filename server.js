const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Serve static files
app.use(express.static(path.join(__dirname)));

// Store messages
let messages = [];

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('New user connected');
    
    // Send existing messages to new user
    socket.emit('previous messages', messages);
    
    // Handle new messages
    socket.on('chat message', (msg) => {
        const message = {
            text: msg.text,
            user: msg.user,
            timestamp: new Date()
        };
        messages.push(message);
        // Broadcast to all connected clients
        io.emit('chat message', message);
    });
    
    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('User disconnected');
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 