# Debug Chat Component
# Shows detailed error information

import streamlit as st
from typing import Optional

def render_debug_chat(user_email: Optional[str] = None, user_display_name: Optional[str] = None):
    """Render a debug chat widget with detailed error information."""

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

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; 
            padding: 0; 
            background: #f5f5f5;
          }}
          
          .chat-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 8px;
            overflow: hidden;
          }}
          
          .chat-header {{
            background: #f8f9fa;
            padding: 12px 16px;
            border-bottom: 1px solid #ddd;
            font-weight: 600;
            color: #333;
          }}
          
          .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: white;
          }}
          
          .message {{
            margin-bottom: 12px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #007bff;
          }}
          
          .message-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
          }}
          
          .message-user {{
            font-weight: 600;
            color: #333;
            font-size: 14px;
          }}
          
          .message-time {{
            color: #666;
            font-size: 12px;
          }}
          
          .message-content {{
            color: #333;
            font-size: 14px;
            line-height: 1.4;
          }}
          
          .chat-input {{
            display: flex;
            padding: 12px 16px;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
            gap: 8px;
          }}
          
          .message-input {{
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            outline: none;
          }}
          
          .message-input:focus {{
            border-color: #007bff;
          }}
          
          .send-button {{
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
          }}
          
          .send-button:hover {{
            background: #0056b3;
          }}
          
          .status {{
            padding: 8px 16px;
            background: #e9ecef;
            color: #666;
            font-size: 12px;
            text-align: center;
            border-top: 1px solid #ddd;
          }}
          
          .status.connected {{
            background: #d4edda;
            color: #155724;
          }}
          
          .status.error {{
            background: #f8d7da;
            color: #721c24;
          }}
          
          .debug-info {{
            padding: 8px 16px;
            background: #fff3cd;
            color: #856404;
            font-size: 11px;
            border-top: 1px solid #ffeaa7;
            max-height: 100px;
            overflow-y: auto;
          }}
        </style>
      </head>
      <body>
        <div class="chat-container">
          <div class="chat-header">
            Debug Chat
          </div>
          <div class="chat-messages" id="messages"></div>
          <div class="status" id="status">Loading...</div>
          <div class="debug-info" id="debugInfo">Debug info will appear here...</div>
          <div class="chat-input">
            <input type="text" class="message-input" id="messageInput" placeholder="Type a message..." />
            <button class="send-button" id="sendButton">Send</button>
          </div>
        </div>

        <script>
          // Configuration
          const SUPABASE_URL = '{safe_url}';
          const SUPABASE_ANON_KEY = '{safe_key}';
          const USER_EMAIL = '{safe_user}';
          const USER_DISPLAY_NAME = '{safe_display_name}';

          let messagesEl = null;
          let messageInput = null;
          let sendButton = null;
          let statusEl = null;
          let debugEl = null;

          function log(message) {{
            console.log(message);
            if (debugEl) {{
              debugEl.innerHTML += '<div>' + new Date().toLocaleTimeString() + ': ' + message + '</div>';
              debugEl.scrollTop = debugEl.scrollHeight;
            }}
          }}

          function formatTime(timestamp) {{
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
          }}

          function addMessage(message) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const isOwnMessage = message.user_email === USER_EMAIL;
            const displayName = isOwnMessage ? USER_DISPLAY_NAME : (message.user_email ? message.user_email.split('@')[0] : 'Anonymous');
            
            messageDiv.innerHTML = `
              <div class="message-header">
                <div class="message-user">${{displayName}}</div>
                <div class="message-time">${{formatTime(message.created_at || message.timestamp)}}</div>
              </div>
              <div class="message-content">${{message.message}}</div>
            `;
            
            messagesEl.appendChild(messageDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }}

          async function loadMessages() {{
            try {{
              log('Loading messages from: ' + SUPABASE_URL + '/rest/v1/tavern_messages');
              
              const response = await fetch(`${{SUPABASE_URL}}/rest/v1/tavern_messages?select=*&order=created_at.asc`, {{
                headers: {{
                  'apikey': SUPABASE_ANON_KEY,
                  'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`,
                  'Content-Type': 'application/json'
                }}
              }});
              
              log('Response status: ' + response.status);
              
              if (!response.ok) {{
                const errorText = await response.text();
                log('Error response: ' + errorText);
                throw new Error('Failed to load messages: ' + response.status + ' ' + errorText);
              }}
              
              const messages = await response.json();
              log('Loaded ' + messages.length + ' messages');
              
              messagesEl.innerHTML = '';
              messages.forEach(msg => addMessage(msg));
              
            }} catch (err) {{
              log('Load messages failed: ' + err.message);
              statusEl.textContent = 'Error loading messages: ' + err.message;
              statusEl.className = 'status error';
            }}
          }}

          async function sendMessage() {{
            const text = messageInput.value.trim();
            if (!text) return;
            
            try {{
              const messageData = {{
                id: crypto.randomUUID(),
                user_email: USER_EMAIL || 'anonymous',
                message: text,
                created_at: new Date().toISOString()
              }};
              
              log('Sending message: ' + JSON.stringify(messageData));
              
              messageInput.value = '';
              
              const response = await fetch(`${{SUPABASE_URL}}/rest/v1/tavern_messages`, {{
                method: 'POST',
                headers: {{
                  'apikey': SUPABASE_ANON_KEY,
                  'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`,
                  'Content-Type': 'application/json',
                  'Prefer': 'return=minimal'
                }},
                body: JSON.stringify(messageData)
              }});

              log('Send response status: ' + response.status);
              
              if (!response.ok) {{
                const errorText = await response.text();
                log('Send error response: ' + errorText);
                throw new Error('Failed to send message: ' + response.status + ' ' + errorText);
              }}

              log('Message sent successfully');
              addMessage(messageData);

            }} catch (err) {{
              log('Send failed: ' + err.message);
              statusEl.textContent = 'Error: ' + err.message;
              statusEl.className = 'status error';
              messageInput.value = text;
            }}
          }}

          function setupEventListeners() {{
            sendButton.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', (e) => {{
              if (e.key === 'Enter') {{
                e.preventDefault();
                sendMessage();
              }}
            }});
          }}

          async function init() {{
            try {{
              messagesEl = document.getElementById('messages');
              messageInput = document.getElementById('messageInput');
              sendButton = document.getElementById('sendButton');
              statusEl = document.getElementById('status');
              debugEl = document.getElementById('debugInfo');

              log('Initializing debug chat...');
              log('User email: ' + USER_EMAIL);
              log('User display name: ' + USER_DISPLAY_NAME);

              setupEventListeners();

              // Load messages
              await loadMessages();
              
              statusEl.textContent = 'Connected';
              statusEl.className = 'status connected';

            }} catch (err) {{
              log('Init failed: ' + err.message);
              statusEl.textContent = 'Error: ' + err.message;
              statusEl.className = 'status error';
            }}
          }}

          // Initialize when page loads
          document.addEventListener('DOMContentLoaded', init);
        </script>
      </body>
    </html>
    """

    import streamlit.components.v1 as components
    components.html(html, height=600)
