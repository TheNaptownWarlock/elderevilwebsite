const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*", // Allow all origins for testing
        methods: ["GET", "POST"]
    }
});

// Serve static files
app.use(express.static(path.join(__dirname)));

// Store messages
let messages = [];

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('New user connected:', socket.id);
    
    // Send a welcome message
    socket.emit('chat message', {
        user: 'System',
        text: 'Welcome to the chat!',
        timestamp: new Date()
    });
    
    // Handle new messages
    socket.on('chat message', (msg) => {
        console.log('Message received:', msg);
        // Broadcast to all connected clients
        io.emit('chat message', {
            user: msg.user,
            text: msg.text,
            timestamp: new Date()
        });
    });
    
    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 