# Real-time Supabase Tavern Chat component
# Renders a small client-side HTML/JS widget that subscribes to the
# `tavern_messages` table via supabase-js and allows posting messages.

import streamlit as st
from typing import Optional


# Real-time Supabase Tavern Chat component
# Renders a messenger-style chat widget that connects to Supabase
# for real-time messaging.

import streamlit as st
from typing import Optional

def render_realtime_tavern_chat(user_email: Optional[str] = None, user_display_name: Optional[str] = None, user_avatar: Optional[str] = None):
    """Render an enhanced Facebook Messenger-style chat widget using Supabase Realtime for messaging.

    Args:
        user_email: optional email to attribute messages to; if not provided, the widget
                   will attempt to use st.session_state.current_user['email'] when available.
        user_display_name: optional display name for the user
        user_avatar: optional avatar emoji/character for the user

    The component expects two secrets in Streamlit: SUPABASE_URL and SUPABASE_ANON_KEY (anon key).
    """

    # Determine user email and display info
    if not user_email:
        try:
            user_email = st.session_state.get('current_user', {}).get('email')
            user_display_name = st.session_state.get('current_user', {}).get('display_name', user_email)
            user_avatar = st.session_state.get('current_user', {}).get('avatar', '👤')
        except Exception:
            user_email = None
            user_display_name = None
            user_avatar = '👤'

    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.warning("Supabase URL / anon key not configured in Streamlit secrets. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        return

    # Safe-escape values for embedding
    safe_url = SUPABASE_URL.replace("\n", "\\n").replace("'", "\'")
    safe_key = SUPABASE_ANON_KEY.replace("\n", "\\n").replace("'", "\'")
    safe_user = (user_email or "").replace("\n", "\\n").replace("'", "\'")
    safe_display_name = (user_display_name or user_email or "Anonymous").replace("\n", "\\n").replace("'", "\'")
    safe_avatar = (user_avatar or "👤").replace("\n", "\\n").replace("'", "\'")

    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js/dist/umd/supabase.min.js"></script>
        <style>
          body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; 
            padding: 0; 
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }}
          
          .chat-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: white;
            border-radius: 12px;
            margin: 8px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
          }}
          
          .chat-header {{
            background: linear-gradient(135deg, #7B2CBF 0%, #9D4EDD 100%);
            color: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          }}
          
          .chat-title {{
            font-size: 18px;
            font-weight: 600;
            margin: 0;
          }}
          
          .online-indicator {{
            width: 8px;
            height: 8px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
          }}
          
          .online-users {{
            position: absolute;
            top: 100%;
            right: 0;
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
            z-index: 1000;
            min-width: 200px;
            max-height: 300px;
            overflow-y: auto;
          }}
          
          .online-users.show {{
            display: block;
          }}
          
          .online-user {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 2px;
          }}
          
          .online-user:hover {{
            background: #f0f2f5;
          }}
          
          .user-status {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
          }}
          
          .user-status.offline {{
            background: #ccc;
          }}
          
          .user-status.typing {{
            background: #FF9800;
            animation: pulse 1s infinite;
          }}
          
          @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
          }}
          
          #chat {{ 
            padding: 16px; 
            flex: 1;
            overflow-y: auto; 
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #f8f9fa;
          }}
          
          #messages {{
            display: flex;
            flex-direction: column-reverse;
            min-height: min-content;
          }}
          
          .message-group {{
            display: flex;
            flex-direction: column;
            margin-bottom: 8px;
          }}
          
          .message-group.sent {{
            align-items: flex-end;
          }}
          
          .message-group.received {{
            align-items: flex-start;
          }}
          
          .msg {{ 
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 70%;
            position: relative;
            word-wrap: break-word;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 2px 0;
          }}
          
          .msg.sent {{
            background: linear-gradient(135deg, #0084ff 0%, #0066cc 100%);
            color: white;
            border-bottom-right-radius: 4px;
          }}
          
          .msg.received {{
            background: white;
            color: #333;
            border: 1px solid #e1e5e9;
            border-bottom-left-radius: 4px;
          }}
          
          .message-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
          }}
          
          .avatar {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #7B2CBF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
            font-weight: bold;
          }}
          
          .username {{
            font-size: 12px;
            font-weight: 600;
            color: #666;
          }}
          
          .sent .username {{
            color: rgba(255,255,255,0.8);
          }}
          
          .message-content {{
            font-size: 14px;
            line-height: 1.4;
          }}
          
          .message-meta {{ 
            color: #999; 
            font-size: 11px;
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
          }}
          
          .sent .message-meta {{
            color: rgba(255,255,255,0.7);
            justify-content: flex-end;
          }}
          
          .message-status {{
            font-size: 10px;
            opacity: 0.8;
          }}
          
          .typing-indicator {{
            display: none;
            padding: 8px 16px;
            color: #666;
            font-style: italic;
            font-size: 12px;
          }}
          
          .typing-indicator.show {{
            display: block;
          }}
          
          .typing-dots {{
            display: inline-block;
            animation: typing 1.4s infinite;
          }}
          
          @keyframes typing {{
            0%, 60%, 100% {{ opacity: 0.3; }}
            30% {{ opacity: 1; }}
          }}
          
          .loading-indicator {{
            display: none;
            text-align: center;
            padding: 16px;
            color: #666;
            font-size: 12px;
          }}
          
          .loading-indicator.show {{
            display: block;
          }}
          
          .loading-spinner {{
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #7B2CBF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
          }}
          
          @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
          }}
          
          #input-row {{ 
            display: flex; 
            gap: 12px; 
            padding: 16px 20px;
            background: white;
            border-top: 1px solid #e4e6eb;
            align-items: center;
          }}
          
          #msg-input {{ 
            flex: 1; 
            padding: 12px 20px;
            font-size: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 24px;
            outline: none;
            background: #f8f9fa;
            transition: all 0.2s ease;
          }}
          
          #msg-input:focus {{
            border-color: #7B2CBF;
            background: white;
            box-shadow: 0 0 0 3px rgba(123, 44, 191, 0.1);
          }}
          
          #send-btn {{ 
            padding: 12px 20px;
            background: linear-gradient(135deg, #7B2CBF 0%, #9D4EDD 100%);
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(123, 44, 191, 0.3);
          }}
          
          #send-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(123, 44, 191, 0.4);
          }}
          
          #send-btn:active {{
            transform: translateY(0);
          }}
          
          #send-btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
          }}
          
          #status {{ 
            color: #666; 
            font-size: 12px; 
            text-align: center; 
            padding: 8px;
            background: rgba(255,255,255,0.95);
            border-bottom: 1px solid #e4e6eb;
          }}
          
          .status-connected {{
            color: #4CAF50;
          }}
          
          .status-error {{
            color: #f44336;
          }}
          
          .emoji-picker {{
            position: absolute;
            bottom: 60px;
            right: 20px;
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
          }}
          
          .emoji-picker.show {{
            display: block;
          }}
          
          .emoji-btn {{
            background: none;
            border: none;
            font-size: 18px;
            padding: 4px;
            cursor: pointer;
            border-radius: 4px;
          }}
          
          .emoji-btn:hover {{
            background: #f0f2f5;
          }}
          
          .search-container {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
            z-index: 1000;
          }}
          
          .search-container.show {{
            display: block;
          }}
          
          .search-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e1e5e9;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 8px;
          }}
          
          .search-results {{
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #e1e5e9;
            border-radius: 6px;
            background: #f8f9fa;
          }}
          
          .search-result {{
            padding: 8px 12px;
            border-bottom: 1px solid #e1e5e9;
            cursor: pointer;
            font-size: 12px;
          }}
          
          .search-result:hover {{
            background: #e1e5e9;
          }}
          
          .search-result.highlighted {{
            background: #7B2CBF;
            color: white;
          }}
          
          .search-result-meta {{
            color: #666;
            font-size: 10px;
            margin-top: 2px;
          }}
          
          .search-no-results {{
            padding: 12px;
            text-align: center;
            color: #666;
            font-size: 12px;
          }}
          
          .search-btn {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 4px;
            border-radius: 4px;
            color: #666;
          }}
          
          .search-btn:hover {{
            background: #f0f2f5;
          }}
          
          .message-reactions {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 4px;
          }}
          
          .reaction {{
            display: inline-flex;
            align-items: center;
            gap: 2px;
            background: #f0f2f5;
            border: 1px solid #e1e5e9;
            border-radius: 12px;
            padding: 2px 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
          }}
          
          .reaction:hover {{
            background: #e1e5e9;
            transform: scale(1.05);
          }}
          
          .reaction.user-reacted {{
            background: #7B2CBF;
            color: white;
            border-color: #7B2CBF;
          }}
          
          .reaction-emoji {{
            font-size: 14px;
          }}
          
          .reaction-count {{
            font-weight: 600;
            font-size: 11px;
          }}
          
          .reaction-picker {{
            position: absolute;
            bottom: 100%;
            left: 0;
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
            z-index: 1000;
          }}
          
          .reaction-picker.show {{
            display: block;
          }}
          
          .reaction-picker-btn {{
            background: none;
            border: none;
            font-size: 16px;
            padding: 4px;
            cursor: pointer;
            border-radius: 4px;
            margin: 2px;
          }}
          
          .reaction-picker-btn:hover {{
            background: #f0f2f5;
          }}
          
          @media (max-width: 768px) {{
            .chat-container {{
              margin: 2px;
              border-radius: 8px;
              height: calc(100vh - 4px);
            }}
            
            .chat-header {{
              padding: 12px 16px;
            }}
            
            .chat-title {{
              font-size: 16px;
            }}
            
            .msg {{
              max-width: 85%;
              padding: 10px 14px;
            }}
            
            .message-header {{
              margin-bottom: 2px;
            }}
            
            .avatar {{
              width: 20px;
              height: 20px;
              font-size: 10px;
            }}
            
            .username {{
              font-size: 11px;
            }}
            
            .message-content {{
              font-size: 13px;
            }}
            
            .message-meta {{
              font-size: 10px;
            }}
            
            #input-row {{
              padding: 12px 16px;
              gap: 8px;
            }}
            
            #msg-input {{
              padding: 10px 16px;
              font-size: 14px;
            }}
            
            #send-btn {{
              padding: 10px 16px;
              font-size: 14px;
            }}
            
            .emoji-picker {{
              bottom: 50px;
              right: 10px;
              left: 10px;
              width: auto;
            }}
            
            .reaction-picker {{
              bottom: 100%;
              left: -10px;
              right: -10px;
              width: auto;
            }}
            
            .online-users {{
              right: 10px;
              left: 10px;
              width: auto;
            }}
            
            .online-user {{
              padding: 6px 8px;
            }}
            
            .typing-indicator {{
              padding: 6px 12px;
              font-size: 11px;
            }}
            
            .loading-indicator {{
              padding: 12px;
              font-size: 11px;
            }}
          }}
          
          @media (max-width: 480px) {{
            .chat-container {{
              margin: 1px;
              height: calc(100vh - 2px);
            }}
            
            .chat-header {{
              padding: 10px 12px;
            }}
            
            .chat-title {{
              font-size: 14px;
            }}
            
            .msg {{
              max-width: 90%;
              padding: 8px 12px;
            }}
            
            .message-content {{
              font-size: 12px;
            }}
            
            #input-row {{
              padding: 10px 12px;
              gap: 6px;
            }}
            
            #msg-input {{
              padding: 8px 12px;
              font-size: 13px;
            }}
            
            #send-btn {{
              padding: 8px 12px;
              font-size: 13px;
            }}
            
            .emoji-btn {{
              padding: 8px 10px;
              font-size: 14px;
            }}
          }}
        </style>
      </head>
      <body>
        <div class="chat-container">
          <div class="chat-header" style="position: relative;">
            <div class="online-indicator" id="online-indicator" onclick="toggleOnlineUsers()"></div>
            <h2 class="chat-title">🍺 The Tavern</h2>
            <button class="search-btn" id="search-btn" onclick="toggleSearch()">🔍</button>
            <div class="online-users" id="online-users">
              <div style="font-weight: 600; margin-bottom: 8px; color: #666;">Online Users</div>
              <div id="online-users-list"></div>
            </div>
            <div class="search-container" id="search-container">
              <input type="text" class="search-input" id="search-input" placeholder="Search messages..." />
              <div class="search-results" id="search-results"></div>
            </div>
          </div>
        <div id="status">Connecting...</div>
        <div id="chat">
            <div class="loading-indicator" id="loading-indicator">
              <div class="loading-spinner"></div>
              Loading messages...
            </div>
          <div id="messages"></div>
            <div class="typing-indicator" id="typing-indicator">
              <span id="typing-text">Someone is typing</span>
              <span class="typing-dots">...</span>
            </div>
        </div>
        <div id="input-row">
          <input id="msg-input" placeholder="Say something in the tavern..." />
            <button id="emoji-btn">😊</button>
            <button id="send-btn">Send</button>
          </div>
        </div>
        
        <div class="emoji-picker" id="emoji-picker">
          <button class="emoji-btn" data-emoji="😀">😀</button>
          <button class="emoji-btn" data-emoji="😂">😂</button>
          <button class="emoji-btn" data-emoji="😍">😍</button>
          <button class="emoji-btn" data-emoji="🤔">🤔</button>
          <button class="emoji-btn" data-emoji="👍">👍</button>
          <button class="emoji-btn" data-emoji="👎">👎</button>
          <button class="emoji-btn" data-emoji="❤️">❤️</button>
          <button class="emoji-btn" data-emoji="🎉">🎉</button>
          <button class="emoji-btn" data-emoji="🍺">🍺</button>
          <button class="emoji-btn" data-emoji="⚔️">⚔️</button>
        </div>

        <script>
          var SUPABASE_URL = '""" + safe_url + """';
          var SUPABASE_ANON_KEY = '""" + safe_key + """';
          var USER_EMAIL = '""" + safe_user + """';
          var USER_DISPLAY_NAME = '""" + safe_display_name + """';
          var USER_AVATAR = '""" + safe_avatar + """';

          var statusEl = document.getElementById('status');
          var chatEl = document.getElementById('chat');
          var inputEl = document.getElementById('msg-input');
          var sendBtn = document.getElementById('send-btn');
          var emojiBtn = document.getElementById('emoji-btn');
          var emojiPicker = document.getElementById('emoji-picker');
          var typingIndicator = document.getElementById('typing-indicator');
          var supabase, channel;
          var typingTimeout;
          var isTyping = false;
          var messageOffset = 0;
          var messageLimit = 50;
          var isLoadingMessages = false;
          var hasMoreMessages = true;

          function formatMessageTime(timestamp) {{
            const date = new Date(timestamp || Date.now());
            const today = new Date();
            const isToday = date.toDateString() === today.toDateString();
            
            if (isToday) {{
              return date.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
            }} else {{
              return date.toLocaleDateString([], {{month: 'short', day: 'numeric'}}) + ' ' + 
                     date.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
            }}
          }}

          var messagesEl = document.getElementById('messages');
          
          function getAvatarForUser(email) {{
            // Simple avatar generation based on email
            const avatars = ['👤', '🧙', '⚔️', '🛡️', '🏰', '🐉', '🧝', '🧚', '🧌', '🎭'];
            if (email === USER_EMAIL) return USER_AVATAR;
            const hash = email.split('').reduce((a, b) => {{
              a = ((a << 5) - a) + b.charCodeAt(0);
              return a & a;
            }}, 0);
            return avatars[Math.abs(hash) % avatars.length];
          }}
          
          function getDisplayNameForUser(email) {{
            if (email === USER_EMAIL) return USER_DISPLAY_NAME;
            return email ? email.split('@')[0] : 'Anonymous';
          }}
          
          function appendMessage(row, prepend = true) {{
            console.log('Appending message:', row);
            const isOwnMessage = row.user_email === USER_EMAIL;
            const avatar = getAvatarForUser(row.user_email);
            const displayName = getDisplayNameForUser(row.user_email);
            const ts = formatMessageTime(row.created_at || row.timestamp);
            
            const messageGroup = document.createElement('div');
            messageGroup.className = 'message-group ' + (isOwnMessage ? 'sent' : 'received');
            messageGroup.dataset.messageId = row.id;
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'msg ' + (isOwnMessage ? 'sent' : 'received');
            
            messageDiv.innerHTML = `
              <div class="message-header">
                <div class="avatar">${{avatar}}</div>
                <div class="username">${{displayName}}</div>
              </div>
              <div class="message-content">${{row.message}}</div>
              <div class="message-reactions" id="reactions-${{row.id}}"></div>
              <div class="message-meta">
                <span>${{ts}}</span>
                <span class="message-status">✓</span>
                <button class="reaction-btn" onclick="toggleReactionPicker('${{row.id}}')" style="background: none; border: none; cursor: pointer; font-size: 12px; color: #666; margin-left: 8px;">😊</button>
              </div>
              <div class="reaction-picker" id="reaction-picker-${{row.id}}">
                <button class="reaction-picker-btn" data-emoji="👍" onclick="addReaction('${{row.id}}', '👍')">👍</button>
                <button class="reaction-picker-btn" data-emoji="❤️" onclick="addReaction('${{row.id}}', '❤️')">❤️</button>
                <button class="reaction-picker-btn" data-emoji="😂" onclick="addReaction('${{row.id}}', '😂')">😂</button>
                <button class="reaction-picker-btn" data-emoji="😮" onclick="addReaction('${{row.id}}', '😮')">😮</button>
                <button class="reaction-picker-btn" data-emoji="😢" onclick="addReaction('${{row.id}}', '😢')">😢</button>
                <button class="reaction-picker-btn" data-emoji="😡" onclick="addReaction('${{row.id}}', '😡')">😡</button>
                <button class="reaction-picker-btn" data-emoji="🎉" onclick="addReaction('${{row.id}}', '🎉')">🎉</button>
                <button class="reaction-picker-btn" data-emoji="🍺" onclick="addReaction('${{row.id}}', '🍺')">🍺</button>
              </div>
            `;
            
            messageGroup.appendChild(messageDiv);
            
            if (prepend) {{
              messagesEl.insertBefore(messageGroup, messagesEl.firstChild);
            }} else {{
              messagesEl.appendChild(messageGroup);
            }}
            
            // Load reactions for this message
            loadMessageReactions(row.id);
          }}

          // Initialize connection and channel
          async function initSupabase() {{
            try {{
              if (supabase) return;  // Already initialized

              console.log('Initializing Supabase client...');
              supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

              // Initial load of messages
              console.log('Loading initial messages...');
              await loadMessages(true);

              // Set up realtime subscription
              console.log('Setting up realtime subscription...');
              
              channel = supabase.channel('realtime-chat');

              channel.on(
                'postgres_changes',
                {
                  event: 'INSERT',
                  schema: 'public',
                  table: 'tavern_messages'
                },
                payload => {
                  console.log('New message received:', payload);
                  
                  // Don't show our own messages as "new" since we already added them
                  if (payload.new.user_email !== USER_EMAIL) {{
                    appendMessage(payload.new, true);

                  // Show temporary status
                  statusEl.textContent = '✨ New message!';
                  statusEl.style.display = 'block';
                  statusEl.style.color = '#4CAF50';
                  setTimeout(() => statusEl.style.display = 'none', 1000);
                  }}
                }
              );
              
              // Subscribe to typing status changes
              channel.on(
                'postgres_changes',
                {
                  event: '*',
                  schema: 'public',
                  table: 'typing_status'
                },
                payload => {
                  console.log('Typing status update:', payload);
                  
                  // Don't show our own typing status
                  if (payload.new && payload.new.user_email !== USER_EMAIL) {
                    // Fetch current typing users
                    fetchTypingUsers();
                    
                    // Refresh online users if the list is open
                    const onlineUsers = document.getElementById('online-users');
                    if (onlineUsers.classList.contains('show')) {
                      loadOnlineUsers();
                    }
                  }
                }
              );
              
              // Subscribe to reaction changes
              channel.on(
                'postgres_changes',
                {
                  event: '*',
                  schema: 'public',
                  table: 'message_reactions'
                },
                payload => {
                  console.log('Reaction update:', payload);
                  
                  // Refresh reactions for the affected message
                  if (payload.new && payload.new.message_id) {
                    loadMessageReactions(payload.new.message_id);
                  }
                }
              );            }} catch (err) {{
              console.error('Supabase init failed:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Connection failed');
              statusEl.style.color = '#d32f2f';
            }}
          }}

          // Typing indicator functions
          async function startTyping() {
            if (!isTyping && USER_EMAIL) {
              isTyping = true;
              console.log('Started typing...');
              
              // Update typing status in Supabase
              try {
                await supabase.from('typing_status').upsert({
                  user_email: USER_EMAIL,
                  is_typing: true,
                  last_seen: new Date().toISOString(),
                  updated_at: new Date().toISOString()
                });
              } catch (err) {
                console.error('Failed to update typing status:', err);
              }
            }
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(stopTyping, 2000);
          }
          
          async function stopTyping() {
            if (isTyping && USER_EMAIL) {
              isTyping = false;
              console.log('Stopped typing...');
              
              // Update typing status in Supabase
              try {
                await supabase.from('typing_status').upsert({
                  user_email: USER_EMAIL,
                  is_typing: false,
                  last_seen: new Date().toISOString(),
                  updated_at: new Date().toISOString()
                });
              } catch (err) {
                console.error('Failed to update typing status:', err);
              }
            }
          }
          
          // Update typing indicator display
          function updateTypingIndicator(typingUsers) {
            const typingText = document.getElementById('typing-text');
            const typingIndicator = document.getElementById('typing-indicator');
            
            if (typingUsers.length > 0) {
              const names = typingUsers.map(user => getDisplayNameForUser(user.user_email)).join(', ');
              typingText.textContent = names + (typingUsers.length === 1 ? ' is typing' : ' are typing');
              typingIndicator.classList.add('show');
            } else {
              typingIndicator.classList.remove('show');
            }
          }
          
          // Load messages with pagination
          async function loadMessages(isInitial = false) {
            if (isLoadingMessages || (!isInitial && !hasMoreMessages)) return;
            
            isLoadingMessages = true;
            const loadingIndicator = document.getElementById('loading-indicator');
            
            if (isInitial) {
              loadingIndicator.classList.add('show');
            }
            
            try {
              const result = await supabase
                .from('tavern_messages')
                .select('*')
                .order('created_at', { ascending: false })
                .range(messageOffset, messageOffset + messageLimit - 1);

              if (result.error) throw result.error;
              
              if (result.data) {
                console.log('Loaded messages:', result.data.length);
                
                if (isInitial) {
                  messagesEl.innerHTML = '';  // Clear loading state
                }
                
                // Append messages in reverse order for proper display
                result.data.forEach(msg => appendMessage(msg, false));
                
                messageOffset += result.data.length;
                hasMoreMessages = result.data.length === messageLimit;
                
                if (isInitial) {
                  // Scroll to bottom on initial load
                  setTimeout(scrollToBottom, 100);
                }
              }
            } catch (err) {
              console.error('Failed to load messages:', err);
              statusEl.textContent = 'Error loading messages: ' + (err.message || 'Unknown error');
              statusEl.style.display = 'block';
              statusEl.style.color = '#d32f2f';
              setTimeout(() => statusEl.style.display = 'none', 3000);
            } finally {
              isLoadingMessages = false;
              loadingIndicator.classList.remove('show');
            }
          }
          
          // Load more messages when scrolling to top
          function setupScrollPagination() {
            const chatContainer = document.getElementById('chat');
            chatContainer.addEventListener('scroll', () => {
              if (chatContainer.scrollTop === 0 && hasMoreMessages && !isLoadingMessages) {
                console.log('Loading more messages...');
                loadMessages(false);
              }
            });
          }
          
          // Fetch current typing users
          async function fetchTypingUsers() {
            try {
              const result = await supabase
                .from('typing_status')
                .select('user_email, is_typing, updated_at')
                .eq('is_typing', true)
                .neq('user_email', USER_EMAIL);
              
              if (result.data) {
                // Filter out users who haven't typed in the last 5 seconds
                const now = new Date();
                const recentTypingUsers = result.data.filter(user => {
                  const lastUpdate = new Date(user.updated_at);
                  return (now - lastUpdate) < 5000; // 5 seconds
                });
                
                updateTypingIndicator(recentTypingUsers);
              }
            } catch (err) {
              console.error('Failed to fetch typing users:', err);
            }
          }
          
          // Online users management
          function toggleOnlineUsers() {
            const onlineUsers = document.getElementById('online-users');
            const searchContainer = document.getElementById('search-container');
            
            // Close search if open
            searchContainer.classList.remove('show');
            
            onlineUsers.classList.toggle('show');
            
            if (onlineUsers.classList.contains('show')) {
              loadOnlineUsers();
            }
          }
          
          // Search functionality
          function toggleSearch() {
            const searchContainer = document.getElementById('search-container');
            const onlineUsers = document.getElementById('online-users');
            
            // Close online users if open
            onlineUsers.classList.remove('show');
            
            searchContainer.classList.toggle('show');
            
            if (searchContainer.classList.contains('show')) {
              document.getElementById('search-input').focus();
            }
          }
          
          async function searchMessages(query) {
            if (!query.trim()) {
              document.getElementById('search-results').innerHTML = '';
              return;
            }
            
            try {
              const result = await supabase
                .from('tavern_messages')
                .select('*')
                .ilike('message', '%' + query + '%')
                .order('created_at', { ascending: false })
                .limit(20);
              
              if (result.data) {
                displaySearchResults(result.data, query);
              }
            } catch (err) {
              console.error('Search failed:', err);
              document.getElementById('search-results').innerHTML = 
                '<div class="search-no-results">Search failed. Please try again.</div>';
            }
          }
          
          function displaySearchResults(messages, query) {
            const resultsContainer = document.getElementById('search-results');
            
            if (messages.length === 0) {
              resultsContainer.innerHTML = '<div class="search-no-results">No messages found</div>';
              return;
            }
            
            resultsContainer.innerHTML = '';
            
            messages.forEach((message, index) => {
              const resultDiv = document.createElement('div');
              resultDiv.className = 'search-result';
              resultDiv.onclick = () => scrollToMessage(message.id);
              
              const highlightedMessage = highlightSearchTerm(message.message, query);
              const timestamp = formatMessageTime(message.created_at);
              const displayName = getDisplayNameForUser(message.user_email);
              
              resultDiv.innerHTML = `
                <div>${{highlightedMessage}}</div>
                <div class="search-result-meta">${{displayName}} • ${{timestamp}}</div>
              `;
              
              resultsContainer.appendChild(resultDiv);
            });
          }
          
          function highlightSearchTerm(text, query) {
            const regex = new RegExp(`(${{query}})`, 'gi');
            return text.replace(regex, '<mark style="background: #FFEB3B; padding: 1px 2px; border-radius: 2px;">$1</mark>');
          }
          
          function scrollToMessage(messageId) {
            const messageElement = document.querySelector(`[data-message-id="${{messageId}}"]`);
            if (messageElement) {
              messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
              messageElement.style.background = '#FFEB3B';
              setTimeout(() => {
                messageElement.style.background = '';
              }, 2000);
            }
            
            // Close search
            document.getElementById('search-container').classList.remove('show');
          }
          
          async function loadOnlineUsers() {
            try {
              const result = await supabase
                .from('typing_status')
                .select('user_email, is_typing, last_seen, updated_at')
                .neq('user_email', USER_EMAIL)
                .order('last_seen', { ascending: false });
              
              if (result.data) {
                const onlineUsersList = document.getElementById('online-users-list');
                onlineUsersList.innerHTML = '';
                
                const now = new Date();
                const onlineThreshold = 30000; // 30 seconds
                
                result.data.forEach(user => {
                  const lastSeen = new Date(user.last_seen);
                  const isOnline = (now - lastSeen) < onlineThreshold;
                  const isTyping = user.is_typing && (now - new Date(user.updated_at)) < 5000;
                  
                  if (isOnline) {
                    const userDiv = document.createElement('div');
                    userDiv.className = 'online-user';
                    
                    let statusClass = 'user-status';
                    if (isTyping) {
                      statusClass += ' typing';
                    } else if (!isOnline) {
                      statusClass += ' offline';
                    }
                    
                    userDiv.innerHTML = `
                      <div class="${{statusClass}}"></div>
                      <div class="avatar" style="width: 20px; height: 20px; font-size: 10px;">${{getAvatarForUser(user.user_email)}}</div>
                      <div style="flex: 1; font-size: 12px;">${{getDisplayNameForUser(user.user_email)}}</div>
                      <div style="font-size: 10px; color: #999;">${{isTyping ? 'typing...' : 'online'}}</div>
                    `;
                    
                    onlineUsersList.appendChild(userDiv);
                  }
                });
                
                if (onlineUsersList.children.length === 0) {
                  onlineUsersList.innerHTML = '<div style="color: #999; font-size: 12px; text-align: center; padding: 8px;">No other users online</div>';
                }
              }
            } catch (err) {
              console.error('Failed to load online users:', err);
            }
          }
          
          // Reaction functions
          function toggleReactionPicker(messageId) {
            const picker = document.getElementById('reaction-picker-' + messageId);
            const allPickers = document.querySelectorAll('.reaction-picker');
            
            // Close all other pickers
            allPickers.forEach(p => {
              if (p.id !== 'reaction-picker-' + messageId) {
                p.classList.remove('show');
              }
            });
            
            // Toggle current picker
            picker.classList.toggle('show');
          }
          
          async function addReaction(messageId, emoji) {
            if (!USER_EMAIL) return;
            
            try {
              const result = await supabase
                .from('message_reactions')
                .upsert({
                  id: messageId + '_' + USER_EMAIL + '_' + emoji,
                  message_id: messageId,
                  user_email: USER_EMAIL,
                  emoji: emoji
                });
              
              if (result.error) throw result.error;
              
              // Close picker
              document.getElementById('reaction-picker-' + messageId).classList.remove('show');
              
              // Refresh reactions for this message
              await loadMessageReactions(messageId);
              
            } catch (err) {
              console.error('Failed to add reaction:', err);
            }
          }
          
          async function loadMessageReactions(messageId) {
            try {
              const result = await supabase
                .from('message_reactions')
                .select('emoji, user_email')
                .eq('message_id', messageId);
              
              if (result.data) {
                const reactionsContainer = document.getElementById('reactions-' + messageId);
                reactionsContainer.innerHTML = '';
                
                // Group reactions by emoji
                const reactionGroups = {};
                result.data.forEach(reaction => {
                  if (!reactionGroups[reaction.emoji]) {
                    reactionGroups[reaction.emoji] = [];
                  }
                  reactionGroups[reaction.emoji].push(reaction.user_email);
                });
                
                // Create reaction buttons
                Object.entries(reactionGroups).forEach(([emoji, users]) => {
                  const hasUserReacted = users.includes(USER_EMAIL);
                  const reactionDiv = document.createElement('div');
                  reactionDiv.className = 'reaction' + (hasUserReacted ? ' user-reacted' : '');
                  reactionDiv.innerHTML = `
                    <span class="reaction-emoji">${{emoji}}</span>
                    <span class="reaction-count">${{users.length}}</span>
                  `;
                  reactionDiv.onclick = () => addReaction(messageId, emoji);
                  reactionsContainer.appendChild(reactionDiv);
                });
              }
            } catch (err) {
              console.error('Failed to load message reactions:', err);
            }
          }

          // Send message handler
          async function sendMessage() {
            const text = inputEl.value.trim();
            if (!text) return;
            
            try {
              console.log('Sending message...');
              
              // Prepare message data
              var messageData = {
                user_email: USER_EMAIL || 'anonymous',
                message: text,
                created_at: new Date().toISOString()
              };
              
              // Clear input and focus
              inputEl.value = '';
              inputEl.focus();
              stopTyping();
              
              // Add message immediately to UI for better UX
              appendMessage(messageData, true);
              
              // Insert message to database
              const result = await supabase.from('tavern_messages')
                .insert([messageData])
                .select()
                .single();

              if (result.error) throw result.error;
              
              console.log('Message sent successfully:', result.data);
              
              // Show temporary success status
              statusEl.textContent = '✨ Message sent!';
              statusEl.style.display = 'block';
              statusEl.style.color = '#4CAF50';
              setTimeout(() => statusEl.style.display = 'none', 1000);

            } catch (err) {
              console.error('Send failed:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Failed to send');
              statusEl.style.display = 'block';
              statusEl.style.color = '#d32f2f';
              setTimeout(() => statusEl.style.display = 'none', 3000);
              
              // Return input text if send failed
              inputEl.value = text;
            }
          }}

          // Initialize and subscribe
          async function initialize() {
            try {
              await initSupabase();
              console.log('Supabase initialized, subscribing to channel...');
              
              const status = await channel.subscribe();
              console.log('Subscription status:', status);
              
              if (status === 'SUBSCRIBED') {
                console.log('Successfully subscribed to realtime updates');
                statusEl.textContent = 'Connected! Messages will appear instantly.';
                statusEl.className = 'status-connected';
                setTimeout(() => statusEl.style.display = 'none', 2000);
                
                // Fetch initial typing users
                fetchTypingUsers();
                
                // Set up scroll pagination
                setupScrollPagination();
                
                // Set up periodic cleanup of old typing statuses and update online users
                setInterval(async () => {
                  try {
                    const fiveSecondsAgo = new Date(Date.now() - 5000).toISOString();
                    await supabase
                      .from('typing_status')
                      .update({ is_typing: false })
                      .lt('updated_at', fiveSecondsAgo);
                    
                    // Update online users list if it's open
                    const onlineUsers = document.getElementById('online-users');
                    if (onlineUsers.classList.contains('show')) {
                      loadOnlineUsers();
                    }
                  } catch (err) {
                    console.error('Failed to cleanup old typing statuses:', err);
                  }
                }, 10000); // Run every 10 seconds
                
              } else {
                console.log('Subscription failed:', status);
                statusEl.textContent = 'Connection failed: ' + status;
                statusEl.style.display = 'block';
                statusEl.style.color = '#d32f2f';
                statusEl.className = 'status-error';
              }

            }} catch (err) {{
              console.error('Initialization error:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Connection failed');
              statusEl.style.display = 'block';
              statusEl.style.color = '#d32f2f';
            }}
          }}

          // Start initialization
          initialize();

          // Emoji picker functionality
          function toggleEmojiPicker() {
            emojiPicker.classList.toggle('show');
          }
          
          function insertEmoji(emoji) {
            inputEl.value += emoji;
            inputEl.focus();
            emojiPicker.classList.remove('show');
            startTyping();
          }

          // Wire up UI handlers
          sendBtn.addEventListener('click', sendMessage);
          emojiBtn.addEventListener('click', toggleEmojiPicker);
          
          // Emoji picker buttons
          document.querySelectorAll('.emoji-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
              insertEmoji(e.target.dataset.emoji);
            });
          });
          
          // Close emoji picker when clicking outside
          document.addEventListener('click', (e) => {
            if (!emojiPicker.contains(e.target) && !emojiBtn.contains(e.target)) {
              emojiPicker.classList.remove('show');
            }
            
            // Close reaction pickers when clicking outside
            if (!e.target.closest('.reaction-picker') && !e.target.closest('.reaction-btn')) {
              document.querySelectorAll('.reaction-picker').forEach(picker => {
                picker.classList.remove('show');
              });
            }
            
            // Close online users list when clicking outside
            if (!e.target.closest('.online-users') && !e.target.closest('#online-indicator')) {
              document.getElementById('online-users').classList.remove('show');
            }
            
            // Close search container when clicking outside
            if (!e.target.closest('.search-container') && !e.target.closest('#search-btn')) {
              document.getElementById('search-container').classList.remove('show');
            }
          });
          
          inputEl.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter' && !e.shiftKey) {{
              e.preventDefault();
              sendMessage();
            }}
          }});
          
          inputEl.addEventListener('input', startTyping);
          
          // Search input event listener
          document.getElementById('search-input').addEventListener('input', (e) => {
            const query = e.target.value;
            if (query.length > 2) {
              searchMessages(query);
            } else {
              document.getElementById('search-results').innerHTML = '';
            }
          });
          
          // Touch-friendly features for mobile
          let touchStartY = 0;
          let touchEndY = 0;
          
          document.addEventListener('touchstart', (e) => {
            touchStartY = e.changedTouches[0].screenY;
          });
          
          document.addEventListener('touchend', (e) => {
            touchEndY = e.changedTouches[0].screenY;
            handleSwipe();
          });
          
          function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartY - touchEndY;
            
            if (Math.abs(diff) > swipeThreshold) {
              if (diff > 0) {
                // Swipe up - close any open pickers
                document.querySelectorAll('.reaction-picker, .emoji-picker, .online-users').forEach(picker => {
                  picker.classList.remove('show');
                });
              }
            }
          }
          
          // Prevent zoom on double tap for mobile
          let lastTouchEnd = 0;
          document.addEventListener('touchend', (e) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
              e.preventDefault();
            }
            lastTouchEnd = now;
          }, false);
          
          // Auto-scroll to bottom when new messages arrive
          function scrollToBottom() {
            const chatContainer = document.getElementById('chat');
            chatContainer.scrollTop = chatContainer.scrollHeight;
          }
          
          // Override appendMessage to include auto-scroll
          const originalAppendMessage = appendMessage;
          appendMessage = function(row, prepend = true) {
            originalAppendMessage(row, prepend);
            setTimeout(scrollToBottom, 100);
          };

          // Cleanup on unload
          window.addEventListener('unload', () => {{
            console.log('Cleaning up...');
            if (channel) {{
              console.log('Unsubscribing from channel');
              channel.unsubscribe();
            }}
          }});
        </script>
      </body>
    </html>
    """

    import streamlit.components.v1 as components
    components.html(html, height=420)
