# Working Simple Chat Component
# Uses a more reliable Supabase initialization approach

import streamlit as st
from typing import Optional

def render_working_chat(user_email: Optional[str] = None, user_display_name: Optional[str] = None, user_avatar: Optional[str] = None, user_class: Optional[str] = None):
    """Render a simple, clean chat widget with real-time updates.
    
    Args:
        user_email: User's email address
        user_display_name: User's display name
        user_avatar: User's avatar emoji
        user_class: User's class name
    """

    # Get user info
    if not user_email:
        try:
            user_email = st.session_state.get('current_user', {}).get('email')
            user_display_name = st.session_state.get('current_user', {}).get('display_name', user_email)
            user_avatar = st.session_state.get('current_user', {}).get('avatar', '🧙‍♂️')
            user_class = st.session_state.get('current_user', {}).get('user_class', 'Adventurer')
        except Exception:
            user_email = None
            user_display_name = None
            user_avatar = '🧙‍♂️'
            user_class = 'Adventurer'

    # Use hardcoded credentials with secrets fallback (same as app.py)
    SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
    
    # Try to get from secrets first, but fall back to hardcoded if needed
    try:
        secrets_url = st.secrets.get("SUPABASE_URL")
        secrets_key = st.secrets.get("SUPABASE_KEY")
        
        if secrets_url and secrets_key and str(secrets_url).strip() and str(secrets_key).strip():
            SUPABASE_URL = str(secrets_url).strip()
            SUPABASE_ANON_KEY = str(secrets_key).strip()
    except Exception:
        pass  # Use hardcoded values
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.warning("Supabase credentials not configured")
        return

    # Safe-escape values
    safe_url = SUPABASE_URL.replace("\n", "\\n").replace("'", "\'")
    safe_key = SUPABASE_ANON_KEY.replace("\n", "\\n").replace("'", "\'")
    safe_user = (user_email or "").replace("\n", "\\n").replace("'", "\'")
    safe_display_name = (user_display_name or user_email or "Anonymous").replace("\n", "\\n").replace("'", "\'")
    safe_avatar = (user_avatar or "🧙‍♂️").replace("\n", "\\n").replace("'", "\'")
    safe_class = (user_class or "Adventurer").replace("\n", "\\n").replace("'", "\'")

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Uncial+Antiqua&family=MedievalSharp&display=swap');
          
          body {{ 
            font-family: 'Cinzel', 'MedievalSharp', serif;
            margin: 0; 
            padding: 0; 
            background: #f5f5f5;
          }}
          
          .chat-container {{
            display: flex;
            flex-direction: column;
            height: calc(100vh - 20px);
            background: linear-gradient(135deg, #F4E4BC 0%, #E6D3A3 50%, #D4C4A8 100%);
            border: 3px solid #8B4513;
            border-radius: 15px;
            margin: 8px;
            overflow: hidden;
            box-shadow: 
                0 0 20px rgba(139, 69, 19, 0.6),
                0 0 40px rgba(160, 82, 45, 0.4),
                0 0 60px rgba(205, 133, 63, 0.2),
                inset 0 1px 3px rgba(255,255,255,0.3);
            position: relative;
          }}
          
          .chat-container::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #8B4513, #A0522D, #CD853F, #A0522D, #8B4513);
            border-radius: 17px;
            z-index: -1;
            animation: glow 3s ease-in-out infinite alternate;
          }}
          
          @keyframes glow {{
            from {{
              box-shadow: 
                  0 0 20px rgba(139, 69, 19, 0.6),
                  0 0 40px rgba(160, 82, 45, 0.4),
                  0 0 60px rgba(205, 133, 63, 0.2);
            }}
            to {{
              box-shadow: 
                  0 0 30px rgba(139, 69, 19, 0.8),
                  0 0 50px rgba(160, 82, 45, 0.6),
                  0 0 70px rgba(205, 133, 63, 0.4);
            }}
          }}
          
          .chat-header {{
            background: linear-gradient(135deg, #8B4513, #A0522D);
            padding: 12px 16px;
            border-bottom: 2px solid #654321;
            font-weight: 600;
            color: #F4E4BC;
            font-family: 'Uncial Antiqua', cursive;
            font-size: 18px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
          }}
          
          .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: linear-gradient(180deg, #F4E4BC 0%, #E6D3A3 100%);
          }}
          
          .message {{
            margin-bottom: 12px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 8px;
            border-left: 4px solid #8B4513;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-family: 'Cinzel', serif;
            position: relative;
            backdrop-filter: blur(1px);
          }}
          
          .message-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
          }}
          
          .message-user {{
            font-weight: 600;
            color: #8B4513;
            font-size: 14px;
            font-family: 'Cinzel', serif;
          }}
          
          .message-class {{
            font-style: italic;
            color: #654321;
            font-size: 12px;
            margin-left: 4px;
          }}
          
          .message-time {{
            color: #8B7355;
            font-size: 11px;
            font-family: 'Cinzel', serif;
          }}
          
          .message-content {{
            color: #2C1810;
            font-size: 14px;
            line-height: 1.5;
            font-family: 'Cinzel', serif;
          }}
          
          .chat-input {{
            display: flex;
            padding: 12px 16px;
            background: linear-gradient(135deg, #8B4513, #A0522D);
            border-top: 2px solid #654321;
            gap: 8px;
          }}
          
          .message-input {{
            flex: 1;
            padding: 10px 14px;
            border: 2px solid #654321;
            border-radius: 6px;
            font-size: 14px;
            font-family: 'Cinzel', serif;
            background: #F4E4BC;
            color: #2C1810;
            outline: none;
          }}
          
          .message-input:focus {{
            border-color: #F4E4BC;
            box-shadow: 0 0 5px rgba(244, 228, 188, 0.5);
          }}
          
          .send-button {{
            padding: 10px 18px;
            background: linear-gradient(135deg, #654321, #8B4513);
            color: #F4E4BC;
            border: 2px solid #654321;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-family: 'Cinzel', serif;
            font-weight: 600;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            transition: all 0.2s ease;
          }}
          
          .send-button:hover {{
            background: linear-gradient(135deg, #8B4513, #A0522D);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
          }}
          
          .status {{
            padding: 8px 16px;
            background: linear-gradient(135deg, #654321, #8B4513);
            color: #F4E4BC;
            font-size: 12px;
            font-family: 'Cinzel', serif;
            text-align: center;
            border-top: 2px solid #654321;
          }}
          
          .status.connected {{
            background: linear-gradient(135deg, #2D5016, #4A7C59);
            color: #E8F5E8;
          }}
          
          .status.error {{
            background: linear-gradient(135deg, #8B0000, #A52A2A);
            color: #FFE4E1;
          }}
        </style>
      </head>
      <body>
        <div class="chat-container">
          <div class="chat-header">
            The Tavern
          </div>
          <div class="chat-messages" id="messages"></div>
          <div class="status" id="status">Loading...</div>
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
          const USER_AVATAR = '{safe_avatar}';
          const USER_CLASS = '{safe_class}';

          // Avatar to class mapping
          const AVATAR_CLASSES = {{
            "🧙‍♂️": "Trash Wizard",
            "⚔️": "Chaos Goblin", 
            "🏹": "Rotten Archer",
            "🛡️": "Self-Righteous Nerd",
            "🗡️": "Stabby Rogue",
            "🔮": "Skooma Sorc",
            "📚": "Da Worm",
            "🎭": "Theatre Kid",
            "🐉": "Scaly Bastard",
            "🦄": "Unicorn Corpse",
            "🔥": "Fire Hazard",
            "❄️": "Buzzkill",
            "🌟": "Special Little Guy",
            "🦅": "Sky Rat",
            "👑": "Mole King",
            "🦊": "Foxy Schmoxy",
            "🐸": "Froggo",
            "🦉": "Pondering Owl",
            "🐺": "Luuupe",
            "🦋": "Cottage Core Wench",
            "🌙": "Astrology Hoe",
            "☀️": "Praiser of da Sun",
            "⚡": "Sparky Lad",
            "🌊": "Catch-a-ride",
            "🌪️": "Disaster Gay",
            "🍄": "Shroom Enjoyer"
          }};

          let supabase = null;
          let messagesEl = null;
          let messageInput = null;
          let sendButton = null;
          let statusEl = null;
          let lastMessageTime = null;
          let refreshInterval = null;

          function formatTime(timestamp) {{
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
          }}

          function addMessage(message) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const isOwnMessage = message.user_email === USER_EMAIL;
            // Use display name from message data if available, otherwise fall back to email parsing
            let displayName = 'Anonymous';
            if (isOwnMessage) {{
              displayName = USER_DISPLAY_NAME;
            }} else if (message.display_name) {{
              displayName = message.display_name;
            }} else if (message.user_name) {{
              displayName = message.user_name;
            }} else if (message.user_email) {{
              displayName = message.user_email.split('@')[0];
            }}
            
            // Get user class from message data or fallback to avatar mapping
            let userClass = message.user_class || 'Adventurer';
            let userAvatar = message.user_avatar || '🧙‍♂️';
            if (message.user_avatar && AVATAR_CLASSES[message.user_avatar]) {{
              userClass = AVATAR_CLASSES[message.user_avatar];
            }}
            
            // Set avatar as background with 50% transparency
            try {{
              const svgData = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='65' font-size='50' text-anchor='middle' x='50' opacity='0.5'>${{userAvatar}}</text></svg>`;
              const encodedSvg = encodeURIComponent(svgData);
              messageDiv.style.backgroundImage = `url("data:image/svg+xml,${{encodedSvg}}")`;
              messageDiv.style.backgroundRepeat = 'no-repeat';
              messageDiv.style.backgroundPosition = 'center center';
              messageDiv.style.backgroundSize = '70px 70px';
            }} catch (emojiError) {{
              console.warn('Error setting avatar background:', emojiError);
              // Fallback: use subtle gray background instead
              messageDiv.style.backgroundColor = 'rgba(200, 200, 200, 0.3)';
            }}
            
            messageDiv.innerHTML = `
              <div class="message-header">
                <div class="message-user">
                  ${{displayName}}<span class="message-class">- ${{userClass}}</span>
                </div>
                <div class="message-time">${{formatTime(message.created_at || message.timestamp)}}</div>
              </div>
              <div class="message-content">${{message.message}}</div>
            `;
            
            messagesEl.appendChild(messageDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }}

          async function loadMessages(showAll = true) {{
            try {{
              console.log('Loading messages from:', `${{SUPABASE_URL}}/rest/v1/tavern_messages`);
              console.log('Using API key:', SUPABASE_ANON_KEY ? 'Present' : 'Missing');
              
              const response = await fetch(`${{SUPABASE_URL}}/rest/v1/tavern_messages?select=*&order=created_at.asc`, {{
                headers: {{
                  'apikey': SUPABASE_ANON_KEY,
                  'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`,
                  'Content-Type': 'application/json'
                }}
              }});
              
              console.log('Response status:', response.status);
              
              if (!response.ok) {{
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`HTTP ${{response.status}}: ${{errorText}}`);
              }}
              
              const messages = await response.json();
              console.log('Loaded', messages.length, 'messages');
              
              if (showAll) {{
                messagesEl.innerHTML = '';
                messages.forEach(msg => {{
                  try {{
                    addMessage(msg);
                  }} catch (msgError) {{
                    console.warn('Error adding message:', msgError, 'Message data:', msg);
                  }}
                }});
                lastMessageTime = messages.length > 0 ? messages[messages.length - 1].created_at : null;
              }} else {{
                // Only add new messages
                const newMessages = messages.filter(msg => 
                  !lastMessageTime || new Date(msg.created_at) > new Date(lastMessageTime)
                );
                newMessages.forEach(msg => {{
                  try {{
                    addMessage(msg);
                  }} catch (msgError) {{
                    console.warn('Error adding new message:', msgError, 'Message data:', msg);
                  }}
                }});
                if (newMessages.length > 0) {{
                  lastMessageTime = newMessages[newMessages.length - 1].created_at;
                }}
              }}
              
            }} catch (err) {{
              console.error('Load messages failed:', err);
              statusEl.textContent = `Error loading messages: ${{err.message}}`;
              statusEl.className = 'status error';
            }}
          }}

          async function checkForNewMessages() {{
            try {{
              // Get all messages and filter client-side to avoid date filtering issues
              const response = await fetch(`${{SUPABASE_URL}}/rest/v1/tavern_messages?select=*&order=created_at.asc`, {{
                headers: {{
                  'apikey': SUPABASE_ANON_KEY,
                  'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`,
                  'Content-Type': 'application/json'
                }}
              }});
              
              if (!response.ok) return;
              
              const messages = await response.json();
              
              // Filter for new messages client-side
              const newMessages = messages.filter(msg => 
                !lastMessageTime || new Date(msg.created_at) > new Date(lastMessageTime)
              );
              
              newMessages.forEach(msg => addMessage(msg));
              
              if (newMessages.length > 0) {{
                lastMessageTime = newMessages[newMessages.length - 1].created_at;
              }}
              
            }} catch (err) {{
              console.error('Check for new messages failed:', err);
            }}
          }}

          async function sendMessage() {{
            const text = messageInput.value.trim();
            if (!text) return;
            
            try {{
              const messageData = {{
                id: crypto.randomUUID(),
                user_email: USER_EMAIL || 'anonymous',
                user_avatar: USER_AVATAR || '🧙‍♂️',
                user_class: USER_CLASS || 'Adventurer',
                message: text,
                created_at: new Date().toISOString()
              }};
              
              messageInput.value = '';
              
              const response = await fetch(`${{SUPABASE_URL}}/rest/v1/tavern_messages`, {{
                method: 'POST',
                headers: {{
                  'apikey': SUPABASE_ANON_KEY,
                  'Authorization': `Bearer ${{SUPABASE_ANON_KEY}}`,
                  'Content-Type': 'application/json'
                }},
                body: JSON.stringify(messageData)
              }});

              if (!response.ok) throw new Error('Failed to send message');

              // Message will be picked up by auto-refresh, no need to add immediately

            }} catch (err) {{
              console.error('Send failed:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Failed to send');
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

              setupEventListeners();

              // Load messages
              await loadMessages();
              
              // Start auto-refresh every 3 seconds
              refreshInterval = setInterval(checkForNewMessages, 3000);
              
              statusEl.textContent = 'Connected';
              statusEl.className = 'status connected';

            }} catch (err) {{
              console.error('Init failed:', err);
              statusEl.textContent = 'Error: ' + (err.message || 'Initialization failed');
              statusEl.className = 'status error';
            }}
          }}

          // Initialize when page loads
          document.addEventListener('DOMContentLoaded', init);
          
          // Cleanup when page unloads
          window.addEventListener('beforeunload', () => {{
            if (refreshInterval) {{
              clearInterval(refreshInterval);
            }}
          }});
        </script>
      </body>
    </html>
    """

    import streamlit.components.v1 as components
    components.html(html, height=500)
