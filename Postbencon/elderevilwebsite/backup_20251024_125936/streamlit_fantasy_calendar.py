# Enhanced Streamlit app with SQLite database
import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
from fantasy_calendar_db import FantasyCalendarDB

# Initialize database
@st.cache_resource
def init_db():
    return FantasyCalendarDB("fantasy_calendar.db")

def main():
    st.set_page_config(
        page_title="🏰 Bencon - Fantasy Calendar",
        page_icon="⚔️",
        layout="wide"
    )
    
    # Initialize database
    db = init_db()
    
    # Custom CSS for fantasy theme
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #4a1f4a, #2d1b69);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .fantasy-card {
        background: rgba(139, 69, 19, 0.1);
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🏰 BENCON ⚔️</h1>
        <p><em>Your Fantasy Calendar & Event System</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for profile management
    with st.sidebar:
        st.header("🧙‍♂️ Your Profile")
        
        # User registration/login
        username = st.text_input("Username", key="username")
        if username:
            if st.button("Create/Login Profile"):
                user_id = db.add_user(username)
                if user_id:
                    st.success(f"Welcome, {username}!")
                    st.session_state.current_user = username
                else:
                    st.session_state.current_user = username
                    st.info(f"Welcome back, {username}!")
        
        # Character class selection
        if username:
            character_class = st.selectbox(
                "Character Class",
                ["Warrior", "Mage", "Rogue", "Cleric", "Warlock", "Bard", "Ranger"]
            )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Calendar and Events section
        st.header("📅 Quest Calendar")
        
        # Event creation
        with st.expander("⚡ Create New Adventure"):
            event_title = st.text_input("Quest Name")
            event_date = st.date_input("Adventure Date", min_value=date.today())
            event_time = st.time_input("Start Time")
            event_desc = st.text_area("Quest Description")
            
            if st.button("🗡️ Create Quest") and username:
                if event_title:
                    event_id = db.create_event(
                        event_title, 
                        event_date.strftime("%Y-%m-%d"),
                        username,
                        event_desc,
                        event_time.strftime("%H:%M")
                    )
                    if event_id:
                        st.success(f"Quest '{event_title}' created!")
                        st.rerun()
        
        # Display events
        st.subheader("🗓️ Upcoming Adventures")
        
        # Date selector
        selected_date = st.date_input("Select Date", value=date.today())
        events = db.get_events(selected_date.strftime("%Y-%m-%d"))
        
        if events:
            for event in events:
                with st.container():
                    st.markdown(f"""
                    <div class="fantasy-card">
                        <h4>⚔️ {event[1]}</h4>
                        <p><strong>🕐 Time:</strong> {event[4] or 'TBD'}</p>
                        <p><strong>👑 Quest Master:</strong> {event[7]}</p>
                        <p><strong>📜 Description:</strong> {event[2] or 'No description'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # RSVP section
                    col_rsvp1, col_rsvp2, col_rsvp3 = st.columns(3)
                    
                    with col_rsvp1:
                        if st.button(f"🗡️ Going!", key=f"yes_{event[0]}") and username:
                            db.rsvp_to_event(event[0], username, 'yes')
                            st.success("RSVP: Going!")
                            st.rerun()
                    
                    with col_rsvp2:
                        if st.button(f"🤔 Maybe", key=f"maybe_{event[0]}") and username:
                            db.rsvp_to_event(event[0], username, 'maybe')
                            st.success("RSVP: Maybe!")
                            st.rerun()
                    
                    with col_rsvp3:
                        if st.button(f"❌ Can't Make It", key=f"no_{event[0]}") and username:
                            db.rsvp_to_event(event[0], username, 'no')
                            st.success("RSVP: Can't make it!")
                            st.rerun()
                    
                    # Show RSVPs
                    rsvps = db.get_rsvps_for_event(event[0])
                    if rsvps:
                        st.write("**Adventurers:**")
                        for rsvp in rsvps:
                            status_emoji = "🗡️" if rsvp[3] == 'yes' else "🤔" if rsvp[3] == 'maybe' else "❌"
                            st.write(f"{status_emoji} {rsvp[5]} ({rsvp[6] or 'Adventurer'})")
        else:
            st.info("No quests scheduled for this date. Create one!")
    
    with col2:
        # Tavern Chat
        st.header("🍺 The Tavern")
        
        # Chat input
        if username:
            chat_message = st.text_input("Send a message to the tavern:", key="chat_input")
            if st.button("📜 Send Message"):
                if chat_message:
                    db.add_tavern_message(username, chat_message)
                    st.success("Message sent!")
                    st.rerun()
        
        # Display recent messages (you'd implement this in the DB class)
        st.info("💬 Tavern chat coming soon!")
        
        # Hottest Bar Goss (Recent Activity)
        st.subheader("🔥 Hottest Bar Goss")
        
        recent_activity = db.get_recent_activity(10)
        if recent_activity:
            for activity in recent_activity:
                activity_time = datetime.fromisoformat(activity[5]).strftime("%m/%d %H:%M")
                st.write(f"**{activity_time}** - {activity[6]}: {activity[3]}")
        else:
            st.info("No recent activity. Be the first to create some excitement!")
    
    # Statistics section
    st.header("📊 Bencon Statistics")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("🗓️ Total Events", len(db.get_events()))
    
    with col_stat2:
        # You could add more stats like total users, RSVPs, etc.
        st.metric("⚔️ Active Adventurers", "Coming Soon")
    
    with col_stat3:
        st.metric("🔥 Recent Activity", len(recent_activity))

if __name__ == "__main__":
    main()