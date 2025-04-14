import streamlit as st
import random
import json
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
    st.experimental_rerun()

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

    # --- Menu Screen ---
    if st.session_state.game_state == "menu":
        st.title("🔐 Password Prowler")
        st.subheader("Choose a difficulty:")
        if st.button("Easy"):
            st.session_state.difficulty = Difficulty.EASY
            st.session_state.password_obj = get_password(st.session_state.data, st.session_state.difficulty)
            st.session_state.game_state = "playing"
            st.experimental_rerun()
        if st.button("Medium"):
            st.session_state.difficulty = Difficulty.MEDIUM
            st.session_state.password_obj = get_password(st.session_state.data, st.session_state.difficulty)
            st.session_state.game_state = "playing"
            st.experimental_rerun()
        if st.button("Hard"):
            st.session_state.difficulty = Difficulty.HARD
            st.session_state.password_obj = get_password(st.session_state.data, st.session_state.difficulty)
            st.session_state.game_state = "playing"
            st.experimental_rerun()

    # --- Game Screen ---
    elif st.session_state.game_state == "playing":
        pwd = st.session_state.password_obj.password
        st.title(f"Game Mode: {st.session_state.difficulty.name}")
        st.subheader(f"Guess the {len(pwd)}-character password!")

        guess = st.text_input("Enter your guess:", key="input_guess", max_chars=len(pwd))

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Submit Guess"):
                if len(guess) == len(pwd):
                    color_codes = get_color_codes(pwd, guess)
                    st.session_state.guesses.append((guess, color_codes))
                    st.session_state.input_guess = ""

                    if all(code == 0 for code in color_codes):
                        st.session_state.game_state = "won"
                        st.session_state.show_fact = True
                        st.experimental_rerun()
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

if __name__ == "__main__":
    main()
