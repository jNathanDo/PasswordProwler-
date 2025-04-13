import streamlit as st
import random
import json

# Enum substitute for difficulty levels
DIFFICULTIES = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3
}


class Password:
    def __init__(self, entry):
        self.password = entry["password"]
        self.difficulty = entry["difficulty"]
        self.hints = entry["hints"]
        self.characteristics = entry["characteristics"]
        self.facts = entry["facts"]


def parse_json():
    with open("passwords.json", "r") as f:
        data = json.load(f)
    return data.get("passwords", [])


def pick_password(difficulty, used_passwords):
    all_pwds = parse_json()
    filtered = [Password(p) for p in all_pwds if p["difficulty"] == difficulty.lower()]

    unused = [p for p in filtered if p.password not in used_passwords]

    if not unused:
        st.warning("All passwords used for this difficulty. Reusing previous ones.")
        unused = filtered

    chosen = random.choice(unused)
    return chosen


def get_char_color(pwd, guess):
    result = []
    for i, char in enumerate(guess):
        if i < len(pwd):
            if char == pwd[i]:
                result.append("🟩")  # green
            elif char.lower() == pwd[i].lower():
                result.append("🟨")  # yellow
            elif char.lower() in pwd.lower():
                result.append("🟧")  # orange
            else:
                result.append("🟥")  # red
        else:
            result.append("⬜")  # guess too long
    return result


# Session state initialization
if "game_state" not in st.session_state:
    st.session_state.game_state = "menu"
    st.session_state.used_passwords = []
    st.session_state.guesses = []
    st.session_state.selected_pwd = None

# Main menu
if st.session_state.game_state == "menu":
    st.title("🔐 Password Prowler")
    st.markdown("Choose a difficulty to start:")

    for label, level in DIFFICULTIES.items():
        if st.button(label):
            pwd = pick_password(label, st.session_state.used_passwords)
            st.session_state.selected_pwd = pwd
            st.session_state.used_passwords.append(pwd.password)
            st.session_state.guesses = []
            st.session_state.game_state = "playing"
            st.experimental_rerun()

# Game loop
elif st.session_state.game_state == "playing":
    pwd = st.session_state.selected_pwd
    st.title(f"Mode: {pwd.difficulty.title()}")

    guess = st.text_input("Enter your guess:")

    if guess:
        result = get_char_color(pwd.password, guess)
        st.session_state.guesses.append((guess, result))
        st.experimental_rerun()

    for g, colors in st.session_state.guesses:
        st.write("".join(colors), f"**{g}**")

    if st.session_state.guesses and st.session_state.guesses[-1][0] == pwd.password:
        st.balloons()
        st.success("🎉 You guessed the password!")
        if st.button("Play Again"):
            st.session_state.game_state = "menu"
            st.experimental_rerun()

# Fallback
else:
    st.session_state.game_state = "menu"
    st.experimental_rerun()
