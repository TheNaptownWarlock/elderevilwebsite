# Simple Real-time Chat Component
# Clean, minimal chat interface with real-time updates

import streamlit as st
from typing import Optional

def render_simple_chat(user_email: Optional[str] = None, user_display_name: Optional[str] = None):
    """Render a simple, clean chat widget with real-time updates.
    
    Args:
        user_email: User's email address
        user_display_name: User's display name
    """

    # Get user info
    if not user_email:
        try:
            user_email = st.session_state.get('current_user', {}).get('email')
            user_display_name = st.session_state.get('current_user', {}).get('display_name', user_email)
        except Exception:
            user_email = None
            user_display_name = None

    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.warning("Supabase credentials not configured. Please update secrets.toml")
        return

    # Safe-escape values
    safe_url = SUPABASE_URL.replace("\n", "\\n").replace("'", "\'")
    safe_key = SUPABASE_ANON_KEY.replace("\n", "\\n").replace("'", "\'")
    safe_user = (user_email or "").replace("\n", "\\n").replace("'", "\'")
    safe_display_name = (user_display_name or user_email or "Anonymous").replace("\n", "\\n").replace("'", "\'")

    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
        <style>
          body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; 
            padding: 0; 
            background: #f5f5f5;
          }
          
          .chat-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 8px;
            overflow: hidden;
          }
          
          .chat-header {
            background: #f8f9fa;
            padding: 12px 16px;
            border-bottom: 1px solid #ddd;
            font-weight: 600;
            color: #333;
          }
          
          .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: white;
          }
          
          .message {
            margin-bottom: 12px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #007bff;
          }
          
          .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
          }
          
          .message-user {
            font-weight: 600;
            color: #333;
            font-size: 14px;
          }
          
          .message-time {
            color: #666;
            font-size: 12px;
          }
          
          .message-content {
            color: #333;
            font-size: 14px;
            line-height: 1.4;
          }
          
          .chat-input {
            display: flex;
            padding: 12px 16px;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
            gap: 8px;
          }
          
          .message-input {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            outline: none;
          }
          
          .message-input:focus {
            border-color: #007bff;
          }
          
          .send-button {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
          }
          
          .send-button:hover {
            background: #0056b3;
          }
          
          .status {
            padding: 8px 16px;
            background: #e9ecef;
            color: #666;
            font-size: 12px;
            text-align: center;
            border-top: 1px solid #ddd;
          }
          
          .status.connected {
            background: #d4edda;
            color: #155724;
          }
          
          .status.error {
            background: #f8d7da;
            color: #721c24;
          }
        </style>
      </head>
      <body>
        <div class="chat-container">
          <div class="chat-header">
            Chat
          </div>
          <div class="chat-messages" id="messages"></div>
          <div class="status" id="status">Connecting...</div>
          <div class="chat-input">
            <input type="text" class="message-input" id="messageInput" placeholder="Type a message..." />
            <button class="send-button" id="sendButton">Send</button>
          </div>
        </div>

        <script>
          var SUPABASE_URL = '""" + safe_url + """';
          var SUPABASE_ANON_KEY = '""" + safe_key + """';
          var USER_EMAIL = '""" + safe_user + """';
          var USER_DISPLAY_NAME = '""" + safe_display_name + """';

          var messagesEl = document.getElementById('messages');
          var messageInput = document.getElementById('messageInput');
          var sendButton = document.getElementById('sendButton');
          var statusEl = document.getElementById('status');
          var supabase, channel;

          function formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
          }

          function addMessage(message) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const isOwnMessage = message.user_email === USER_EMAIL;
            const displayName = isOwnMessage ? USER_DISPLAY_NAME : (message.user_email ? message.user_email.split('@')[0] : 'Anonymous');
            
            messageDiv.innerHTML = `
              <div class="message-header">
                <div class="message-user">${displayName}</div>
                <div class="message-time">${formatTime(message.created_at || message.timestamp)}</div>
              </div>
              <div class="message-content">${message.message}</div>
            `;
            
            messagesEl.appendChild(messageDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }

          async function initSupabase() {
            try {
              if (supabase) return;

              // Wait for supabase to be available
              if (typeof window.supabase === 'undefined') {
                statusEl.textContent = 'Loading Supabase...';
                await new Promise(resolve => setTimeout(resolve, 1000));
                if (typeof window.supabase === 'undefined') {
                  throw new Error('Supabase library not loaded');
                }
              }

              supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

              // Load existing messages
              const result = await supabase
                .from('tavern_messages')
                .select('*')
                .order('created_at', { ascending: true })
                .limit(50);

              if (result.data) {
                messagesEl.innerHTML = '';
                result.data.forEach(msg => addMessage(msg));
              }

              // Set up real-time subscription
              channel = supabase.channel('simple-chat');
              
              channel.on(
                'postgres_changes',
                {
                  event: 'INSERT',
                  schema: 'public',
                  table: 'tavern_messages'
                },
                payload => {
                  addMessage(payload.new);
                }
              );

              const status = await channel.subscribe();
              
              if (status === 'SUBSCRIBED') {
                statusEl.textContent = 'Connected';
                statusEl.className = 'status connected';
              } else {
                statusEl.textContent = 'Connection failed';
                statusEl.className = 'status error';
              }

            } catch (err) {
              console.error('Supabase init failed:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Connection failed');
              statusEl.className = 'status error';
            }
          }

          async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;
            
            if (!supabase) {
              statusEl.textContent = 'Initializing...';
              await initSupabase();
            }
            
            try {
              const messageData = {
                user_email: USER_EMAIL || 'anonymous',
                message: text,
                created_at: new Date().toISOString()
              };
              
              messageInput.value = '';
              
              const result = await supabase
                .from('tavern_messages')
                .insert([messageData])
                .select()
                .single();

              if (result.error) throw result.error;

            } catch (err) {
              console.error('Send failed:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Failed to send');
              statusEl.className = 'status error';
              messageInput.value = text;
            }
          }

          // Event listeners
          sendButton.addEventListener('click', sendMessage);
          messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              sendMessage();
            }
          });

          // Initialize
          initSupabase();
        </script>
      </body>
    </html>
    """

    import streamlit.components.v1 as components
    components.html(html, height=500)
