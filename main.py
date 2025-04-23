import streamlit as st
import random
import json
import time
from enum import Enum

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Password:
    def __init__(self):
        self.password = ""
        self.difficulty = ""
        self.hints = []
        self.characteristics = []
        self.facts = []

    def load_from_dict(self, entry):
        self.password = entry["password"]
        self.difficulty = entry["difficulty"]
        self.hints = entry.get("hints", [])
        self.characteristics = entry.get("characteristics", [])
        self.facts = entry.get("facts", [])

def parse_json():
    try:
        with open("passwords.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error reading passwords.json: {e}")
        return {}

def get_password(data, diff):
    entries = [entry for entry in data.get("passwords", []) if entry["difficulty"] == diff.name.lower()]
    if not entries:
        return None
    chosen = random.choice(entries)
    pwd_obj = Password()
    pwd_obj.load_from_dict(chosen)
    return pwd_obj

def get_color_codes(password, guess):
    color_codes = []
    for i, char in enumerate(guess):
        if i < len(password):
            if char == password[i]:
                color_codes.append(0)  # Correct
            elif char.lower() == password[i].lower():
                color_codes.append(1)  # Right char, wrong case
            elif char.lower() in password.lower():
                color_codes.append(2)  # In password, wrong spot
            else:
                color_codes.append(3)  # Not in password
        else:
            color_codes.append(3)
    return color_codes

def color_map(code):
    return ["green", "yellow", "orange", "red"][code]

def reset_game():
    st.session_state.game_state = "menu"
    st.session_state.password_obj = None
    st.session_state.guesses = []
    st.session_state.input_guess = ""
    st.session_state.difficulty = None
    st.session_state.hint_index = 0
    st.session_state.show_hint = False
    st.session_state.show_fact = False
    st.session_state.start_time = None
    st.session_state.remaining_time = 180
    st.session_state.guess_limit = 15

def show_settings():
    st.title("⚙️ Settings")
    st.session_state.timer_enabled = st.checkbox("Enable Timer", value=st.session_state.get("timer_enabled", False))
    st.session_state.guess_limit_enabled = st.checkbox("Enable Guess Limit", value=st.session_state.get("guess_limit_enabled", False))

    st.info("These settings will apply when you start a new game from the Home screen.")

def show_rules():
    st.title("📜 Rules")
    st.markdown("""
    - Choose a difficulty to start the game.
    - You will see how many letters are in the password.
    - Type in your guess and submit it.
    - The color code will tell you how accurate your guess is:
        - 🟩 **Green**: Correct letter in the correct spot.
        - 🟨 **Yellow**: Correct letter, wrong case.
        - 🟧 **Orange**: Letter is in the password but wrong spot.
        - 🟥 **Red**: Letter not in the password.
    - Use the **Hint** button for help (limited!).
    """)

def show_objective():
    st.title("🎯 Objective")
    st.markdown("""
    Your mission is to guess the secret password based on color feedback.
    
    Each guess brings you closer, and hints help you uncover the password’s secrets.

    Can you outsmart the system and become the ultimate **Password Prowler**?
    """)
def run_game_logic():
    if st.session_state.get("use_timer", False):
        st.warning(f"⏳ Time Left: {st.session_state.remaining_time} seconds")

    if st.session_state.get("use_guess_limit", False):
        guesses_left = st.session_state.guess_limit - len(st.session_state.guesses)
        st.info(f"🧠 Guesses Left: {guesses_left}")
# Guess limit check
if st.session_state.get("use_guess_limit", False):
    if len(st.session_state.guesses) >= st.session_state.guess_limit:
        st.session_state.game_state = "failed"
    # --- Menu Screen ---
    if st.session_state.game_state == "menu":
        st.title("🔐 Password Prowler")
        st.subheader("Choose a difficulty:")
        if st.button("Easy"):
            st.session_state.difficulty = Difficulty.EASY
            st.session_state.password_obj = get_password(st.session_state.data, st.session_state.difficulty)
            st.session_state.game_state = "playing"
        if st.button("Medium"):
            st.session_state.difficulty = Difficulty.MEDIUM
            st.session_state.password_obj = get_password(st.session_state.data, st.session_state.difficulty)
            st.session_state.game_state = "playing"
        if st.button("Hard"):
            st.session_state.difficulty = Difficulty.HARD
            st.session_state.password_obj = get_password(st.session_state.data, st.session_state.difficulty)
            st.session_state.game_state = "playing"

    # --- Game Screen ---
    elif st.session_state.game_state == "playing":
        pwd = st.session_state.password_obj.password
        st.title(f"Game Mode: {st.session_state.difficulty.name}")
        st.subheader(f"Guess the {len(pwd)}-character password!")
        if st.session_state.get("use_timer", False):
            st.warning(f"⏳ Time Left: {st.session_state.remaining_time} seconds")

        if st.session_state.get("use_guess_limit", False):
            guesses_left = st.session_state.guess_limit - len(st.session_state.guesses)
            st.info(f"🧠 Guesses Left: {guesses_left}")  where would this go

        guess = st.text_input("Enter your guess:", key="input_guess", max_chars=len(pwd))

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Submit Guess"):
                if len(guess) == len(pwd):
                    color_codes = get_color_codes(pwd, guess)
                    st.session_state.guesses.append((guess, color_codes))
                    if all(code == 0 for code in color_codes):
                        st.session_state.game_state = "won"
                        st.session_state.show_fact = True
                else:
                    st.warning(f"Guess must be {len(pwd)} characters.")
        with col2:
            if st.button("Hint"):
                st.session_state.show_hint = True
                st.session_state.hint_index = min(
                    st.session_state.hint_index + 1,
                    len(st.session_state.password_obj.hints)
                )
        with col3:
            if st.button("🔙 Back to Menu"):
                reset_game()

        # Display previous guesses
        st.write("### Previous Guesses:")
        for guess_str, codes in st.session_state.guesses[-7:]:
            cols = st.columns(len(guess_str))
            for i, c in enumerate(guess_str):
                with cols[i]:
                    st.markdown(
                        f'<div style="background-color:{color_map(codes[i])}; color: white; text-align: center; border-radius: 5px; padding: 10px;">{c}</div>',
                        unsafe_allow_html=True
                    )

        # Show hints if requested
        if st.session_state.show_hint and st.session_state.hint_index > 0:
            st.info("### Hint:")
            for i in range(st.session_state.hint_index):
                if i < len(st.session_state.password_obj.hints):
                    st.write(f"- {st.session_state.password_obj.hints[i]}")

    # --- Win Screen ---
    elif st.session_state.game_state == "won":
        st.title("🎉 You Win!")
        st.success(f"Password: `{st.session_state.password_obj.password}`")
        if st.session_state.show_fact and st.session_state.password_obj.facts:
            st.subheader("🔎 Did you know?")
            st.write(random.choice(st.session_state.password_obj.facts))

        if st.button("Play Again"):
            reset_game()
    elif st.session_state.game_state == "failed":
        st.title("❌ Game Over")
        if st.session_state.get("use_timer", False) and st.session_state.remaining_time == 0:
            st.error("You ran out of time!")
        elif st.session_state.get("use_guess_limit", False):
            st.error("You ran out of guesses!")
        else:
            st.error("Game ended.")

    st.warning(f"The password was: `{st.session_state.password_obj.password}`")

    if st.button("Play Again"):
        reset_game()

def main():
    st.set_page_config(page_title="Password Prowler", layout="centered")

    # --- Initial Session State ---
    if "game_state" not in st.session_state:
        st.session_state.game_state = "menu"
        st.session_state.guesses = []
        st.session_state.data = parse_json()
        st.session_state.password_obj = None
        st.session_state.input_guess = ""
        st.session_state.difficulty = None
        st.session_state.hint_index = 0
        st.session_state.show_hint = False
        st.session_state.show_fact = False
        st.session_state.timer_enabled = False
        st.session_state.guess_limit_enabled = False

    # --- Sidebar Navigation ---
    nav = st.sidebar.selectbox("📋 Navigate", ["Home", "Settings", "Rules", "Objective"])

    if nav == "Settings":
        show_settings()
    elif nav == "Rules":
        show_rules()
    elif nav == "Objective":
        show_objective()
    else:
        # --- Settings Screen ---
        if st.session_state.game_state == "settings":
            st.title("⚙️ Game Settings")
        st.session_state.use_timer = st.checkbox("Enable Timer (60 seconds)", value=st.session_state.get("use_timer", False))
        st.session_state.use_guess_limit = st.checkbox("Enable Guess Limit (7 guesses)", value=st.session_state.get("use_guess_limit", False))
        if st.button("Back to Menu"):
            st.session_state.game_state = "menu"
        run_game_logic()
        

 

if __name__ == "__main__":
    main()
