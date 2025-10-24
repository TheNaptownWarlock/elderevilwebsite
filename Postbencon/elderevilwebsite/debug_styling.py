#!/usr/bin/env python3
"""
Debug script to test CSS injection and styling issues
"""

import streamlit as st

st.title("🔍 CSS Debug Tool")

# Test 1: Simple CSS injection
st.subheader("Test 1: Simple CSS")
st.components.v1.html("""
<style>
.test-button {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
}
</style>
<button class="test-button">Test Button</button>
""", height=100)

# Test 2: Streamlit button with CSS override
st.subheader("Test 2: Streamlit Button Override")
st.components.v1.html("""
<style>
/* Target ALL buttons */
button {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
}
</style>
""", height=0)

if st.button("Test Streamlit Button"):
    st.write("Button clicked!")

# Test 3: JavaScript force styling
st.subheader("Test 3: JavaScript Force Styling")
st.components.v1.html("""
<script>
function forceStyle() {
    const buttons = document.querySelectorAll('button');
    console.log('Found buttons:', buttons.length);
    buttons.forEach((button, index) => {
        console.log(`Button ${index}:`, button);
        button.style.background = 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%)';
        button.style.color = '#FFFACD';
        button.style.border = '2px solid #654321';
        button.style.borderRadius = '8px';
        button.style.fontFamily = "'Cinzel', serif";
        button.style.fontWeight = 'bold';
        button.style.textShadow = '1px 1px 2px rgba(0,0,0,0.8)';
    });
}

// Run immediately and every second
forceStyle();
setInterval(forceStyle, 1000);

// Also run when DOM changes
const observer = new MutationObserver(forceStyle);
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", height=0)

if st.button("Test JavaScript Forced Button"):
    st.write("JavaScript forced button clicked!")

# Test 4: Check what CSS is actually loaded
st.subheader("Test 4: CSS Debug Info")
st.components.v1.html("""
<script>
function debugCSS() {
    const stylesheets = document.styleSheets;
    console.log('Total stylesheets:', stylesheets.length);
    
    for (let i = 0; i < stylesheets.length; i++) {
        try {
            const rules = stylesheets[i].cssRules || stylesheets[i].rules;
            console.log(`Stylesheet ${i}:`, stylesheets[i].href || 'inline', 'Rules:', rules.length);
        } catch (e) {
            console.log(`Stylesheet ${i}:`, stylesheets[i].href || 'inline', 'Error accessing rules:', e.message);
        }
    }
    
    // Check for our specific CSS
    const buttons = document.querySelectorAll('button');
    if (buttons.length > 0) {
        const computedStyle = window.getComputedStyle(buttons[0]);
        console.log('Button computed styles:');
        console.log('background:', computedStyle.background);
        console.log('color:', computedStyle.color);
        console.log('border:', computedStyle.border);
        console.log('font-family:', computedStyle.fontFamily);
    }
}

debugCSS();
</script>
<div id="debug-info">Check browser console for CSS debug info</div>
""", height=100)

# Test 5: Form with styling
st.subheader("Test 5: Form Styling")
with st.form("test_form"):
    st.text_input("Test Input")
    st.selectbox("Test Select", ["Option 1", "Option 2"])
    st.radio("Test Radio", ["Option A", "Option B"])
    submitted = st.form_submit_button("Submit Form")

if submitted:
    st.write("Form submitted!")

st.write("**Instructions:**")
st.write("1. Open browser developer tools (F12)")
st.write("2. Go to Console tab")
st.write("3. Look for any error messages")
st.write("4. Check if CSS is being applied")
st.write("5. Look for 'Found buttons' and styling logs")
