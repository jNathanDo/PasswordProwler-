import streamlit as st
import random
import json

# Load passwords from JSON
with open("passwords.json", "r") as f:
    password_data = json.load(f)["passwords"]

# Group passwords by difficulty
passwords_by_difficulty = {
    "easy": [p for p in password_data if p["difficulty"] == "easy"],
    "medium": [p for p in password_data if p["difficulty"] == "medium"],
    "hard": [p for p in password_data if p["difficulty"] == "hard"]
}

st.title("🔐 Password Prowler")

# Difficulty selection
difficulty = st.selectbox("Choose a difficulty:", ["easy", "medium", "hard"])

# Session state to persist game info
if "selected_password" not in st.session_state:
    st.session_state.selected_password = None
if "used_passwords" not in st.session_state:
    st.session_state.used_passwords = set()

# Pick a new password if none or difficulty changed
available = [p for p in passwords_by_difficulty[difficulty] if p["password"] not in st.session_state.used_passwords]
if not available:
    st.write("No more unused passwords available for this difficulty.")
    st.stop()

# Let user start a new game
if st.button("New Password") or st.session_state.selected_password is None:
    chosen = random.choice(available)
    st.session_state.selected_password = chosen
    st.session_state.used_passwords.add(chosen["password"])

# Display hints
pw = st.session_state.selected_password
if pw:
    st.subheader("Hints:")
    for hint in pw["hints"]:
        st.write(f"- {hint}")

# User guess input
guess = st.text_input("Enter your password guess:")

# Submit guess
if st.button("Submit Guess"):
    if guess.strip() == pw["password"]:
        st.success("✅ Correct!")
        st.markdown("### Facts:")
        for fact in pw["facts"]:
            st.write(f"- {fact}")
    else:
        st.error("❌ Incorrect, try again!")
