# Email Service for Bencon Fantasy Calendar
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
from datetime import datetime, timedelta
import streamlit as st

def generate_verification_code(length=6):
    """Generate a random verification code"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_reset_token(length=32):
    """Generate a random reset token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_verification_email(email, verification_code):
    """Send verification email to user"""
    try:
        # Email configuration - you'll need to set these in your secrets.toml
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)
        sender_email = st.secrets.get("SENDER_EMAIL", "")
        sender_password = st.secrets.get("SENDER_PASSWORD", "")
        
        if not sender_email or not sender_password:
            st.error("Email configuration not found. Please set SMTP credentials in secrets.toml")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "🏰 Bencon Fantasy Calendar - Email Verification"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f1e8; padding: 20px;">
            <div style="background-color: #8B4513; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h1>🏰 Welcome to Bencon Fantasy Calendar! 🏰</h1>
            </div>
            <div style="background-color: white; padding: 20px; margin: 20px 0; border-radius: 10px; border-left: 5px solid #8B4513;">
                <h2>Email Verification Required</h2>
                <p>Greetings, brave adventurer!</p>
                <p>To complete your registration and enter the realm, please use the verification code below:</p>
                <div style="background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 3px; border-radius: 5px; margin: 20px 0;">
                    {verification_code}
                </div>
                <p>This code will expire in 15 minutes.</p>
                <p>If you didn't create an account with us, please ignore this email.</p>
            </div>
            <div style="text-align: center; color: #666; font-size: 12px;">
                <p>May your adventures be legendary! ⚔️</p>
                <p>Bencon Fantasy Calendar Team</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to send verification email: {e}")
        return False

def send_password_reset_email(email, reset_token):
    """Send password reset email to user"""
    try:
        # Email configuration
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)
        sender_email = st.secrets.get("SENDER_EMAIL", "")
        sender_password = st.secrets.get("SENDER_PASSWORD", "")
        
        if not sender_email or not sender_password:
            st.error("Email configuration not found. Please set SMTP credentials in secrets.toml")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "🏰 Bencon Fantasy Calendar - Password Reset"
        
        # Reset URL (you'll need to replace with your actual domain)
        reset_url = f"https://your-domain.com/reset-password?token={reset_token}&email={email}"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f1e8; padding: 20px;">
            <div style="background-color: #8B4513; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h1>🏰 Password Reset Request 🏰</h1>
            </div>
            <div style="background-color: white; padding: 20px; margin: 20px 0; border-radius: 10px; border-left: 5px solid #8B4513;">
                <h2>Reset Your Password</h2>
                <p>Greetings, brave adventurer!</p>
                <p>We received a request to reset your password for your Bencon Fantasy Calendar account.</p>
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #8B4513; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request a password reset, please ignore this email.</p>
            </div>
            <div style="text-align: center; color: #666; font-size: 12px;">
                <p>May your adventures be legendary! ⚔️</p>
                <p>Bencon Fantasy Calendar Team</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to send password reset email: {e}")
        return False
