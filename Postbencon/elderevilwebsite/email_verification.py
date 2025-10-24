import smtplib
import secrets
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import streamlit as st
import hashlib

# Email configuration (you'll need to set these up)
EMAIL_HOST = "smtp.gmail.com"  # or your email provider
EMAIL_PORT = 587
EMAIL_USERNAME = st.secrets.get("EMAIL_USERNAME", "")  # Set in Streamlit secrets
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")  # Set in Streamlit secrets

def init_email_verification_tables():
    """Add email verification tables to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Email verification tokens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_verifications (
        email TEXT PRIMARY KEY,
        token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        verified BOOLEAN DEFAULT 0
    )
    ''')
    
    # Password reset tokens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS password_resets (
        email TEXT,
        token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        used BOOLEAN DEFAULT 0
    )
    ''')
    
    # Add email_verified column to users table if it doesn't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

def send_verification_email(email, token):
    """Send email verification link"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = email
        msg['Subject'] = "🏰 Verify Your Bencon Calendar Account"
        
        # Get the app URL (will work for both local and deployed)
        app_url = st.secrets.get("APP_URL", "http://localhost:8502")
        
        body = f"""
        <html>
        <body style="font-family: 'Cinzel', serif; background: linear-gradient(135deg, #2D1B69 0%, #1A1A2E 100%); color: #FFFACD; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #4A148C; border: 3px solid #7B2CBF; border-radius: 15px; padding: 30px;">
                <h1 style="color: #E0AAFF; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                    🏰 Welcome to Bencon Calendar! 🏰
                </h1>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Greetings, brave adventurer! Your quest to join our tavern community is almost complete.
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Click the magical link below to verify your email and unlock access to all our festivities:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}?verify_token={token}" 
                       style="background: linear-gradient(135deg, #7B2CBF 0%, #9D4EDD 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 25px; font-weight: bold; font-size: 18px;
                              box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                        ✨ Verify My Account ✨
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #C8A2C8;">
                    This link expires in 24 hours. If you didn't create this account, you can safely ignore this email.
                </p>
                
                <hr style="border: 1px solid #7B2CBF; margin: 20px 0;">
                
                <p style="text-align: center; font-style: italic; color: #E0AAFF;">
                    May your dice roll high! 🎲<br>
                    The Bencon Calendar Team
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def send_password_reset_email(email, token):
    """Send password reset link"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = email
        msg['Subject'] = "🔑 Reset Your Bencon Calendar Password"
        
        app_url = st.secrets.get("APP_URL", "http://localhost:8502")
        
        body = f"""
        <html>
        <body style="font-family: 'Cinzel', serif; background: linear-gradient(135deg, #2D1B69 0%, #1A1A2E 100%); color: #FFFACD; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #4A148C; border: 3px solid #7B2CBF; border-radius: 15px; padding: 30px;">
                <h1 style="color: #E0AAFF; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                    🔑 Password Reset Request 🔑
                </h1>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    A password reset was requested for your Bencon Calendar account.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}?reset_token={token}" 
                       style="background: linear-gradient(135deg, #7B2CBF 0%, #9D4EDD 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 25px; font-weight: bold; font-size: 18px;
                              box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                        🔓 Reset Password 🔓
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #C8A2C8;">
                    This link expires in 1 hour. If you didn't request this reset, ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Failed to send reset email: {e}")
        return False

def create_verification_token(email):
    """Create email verification token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO email_verifications (email, token, expires_at, verified)
    VALUES (?, ?, ?, 0)
    ''', (email, token, expires_at))
    
    conn.commit()
    conn.close()
    
    return token

def verify_email_token(token):
    """Verify email token and activate account"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT email FROM email_verifications 
    WHERE token = ? AND expires_at > ? AND verified = 0
    ''', (token, datetime.now()))
    
    result = cursor.fetchone()
    
    if result:
        email = result[0]
        # Mark as verified
        cursor.execute('''
        UPDATE email_verifications SET verified = 1 WHERE token = ?
        ''', (token,))
        
        # Mark user as verified
        cursor.execute('''
        UPDATE users SET email_verified = 1 WHERE email = ?
        ''', (email,))
        
        conn.commit()
        conn.close()
        return email
    
    conn.close()
    return None

def create_password_reset_token(email):
    """Create password reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO password_resets (email, token, expires_at, used)
    VALUES (?, ?, ?, 0)
    ''', (email, token, expires_at))
    
    conn.commit()
    conn.close()
    
    return token

def verify_reset_token(token):
    """Verify password reset token"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT email FROM password_resets 
    WHERE token = ? AND expires_at > ? AND used = 0
    ''', (token, datetime.now()))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def use_reset_token(token):
    """Mark reset token as used"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE password_resets SET used = 1 WHERE token = ?
    ''', (token,))
    
    conn.commit()
    conn.close()

def reset_password(email, new_password):
    """Reset user password"""
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE users SET password_hash = ? WHERE email = ?
    ''', (password_hash, email))
    
    conn.commit()
    conn.close()