def set_difficulty(diff):
    st.session_state.difficulty = diff
    st.session_state.password_obj = get_password(st.session_state.data, diff)
    st.session_state.guesses = []
    st.session_state.show_hint = False
    st.session_state.hint_index = 0
    st.session_state.start_time = time.time() if st.session_state.get("timer_enabled") else None
    st.session_state.remaining_time = 180 if st.session_state.get("timer_enabled") else None
    st.session_state.game_state = "playing"
    st.rerun()

def submit_guess():
    guess = st.session_state.input_guess.strip()
    if guess:
        st.session_state.guesses.append(guess)
        st.session_state.input_guess = ""
        if guess == st.session_state.password_obj.password:
            st.session_state.game_state = "won"
        elif st.session_state.get("guess_limit_enabled") and len(st.session_state.guesses) >= st.session_state.guess_limit:
            st.session_state.game_state = "failed"
        elif st.session_state.get("timer_enabled") and st.session_state.remaining_time <= 0:
            st.session_state.game_state = "failed"
    st.rerun()

def show_hint():
    st.session_state.show_hint = True
    st.rerun()

def show_fact():
    st.session_state.show_fact = True
    st.rerun()

def run_game_logic():
    # Timer check
    if st.session_state.get("timer_enabled", False):
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        elapsed = time.time() - st.session_state.start_time
        st.session_state.remaining_time = max(0, 180 - int(elapsed))
        st.warning(f"⏳ Time Left: {st.session_state.remaining_time} seconds")
        if st.session_state.remaining_time <= 0:
            st.session_state.game_state = "failed"
            st.rerun()

    # Guess limit check
    if st.session_state.get("guess_limit_enabled", False):
        guess_limit = st.session_state.get("guess_limit", 15)
        st.session_state.guess_limit = guess_limit
        guesses_left = guess_limit - len(st.session_state.guesses)
        st.info(f" Guesses Left: {guesses_left}")
        if guesses_left <= 0:
            st.session_state.game_state = "failed"
            st.rerun()

    # --- Menu Screen ---
    if st.session_state.game_state == "menu":
        st.title("🔐 Password Prowler")
        st.subheader("Choose a difficulty:")
        st.button("Easy", on_click=set_difficulty, args=(Difficulty.EASY,))
        st.button("Medium", on_click=set_difficulty, args=(Difficulty.MEDIUM,))
        st.button("Hard", on_click=set_difficulty, args=(Difficulty.HARD,))

    # --- Playing Screen ---
    elif st.session_state.game_state == "playing":
        st.subheader(f"Difficulty: {st.session_state.difficulty.name}")
        st.write(f"Password length: {len(st.session_state.password_obj.password)}")

        guess = st.text_input("Enter your guess", key="input_guess")
        st.button("Submit", on_click=submit_guess)
        st.button("Hint", on_click=show_hint)
        st.button("Fact", on_click=show_fact)

        for past_guess in st.session_state.guesses:
            colors = get_color_codes(st.session_state.password_obj.password, past_guess)
            color_blocks = "".join(
                f":{color_map(code)}[ {char} ]" for char, code in zip(past_guess, colors)
            )
            st.markdown(color_blocks)

        if st.session_state.show_hint and st.session_state.hint_index < len(st.session_state.password_obj.hints):
            st.info(f"💡 Hint: {st.session_state.password_obj.hints[st.session_state.hint_index]}")
            st.session_state.hint_index += 1

        if st.session_state.show_fact and st.session_state.password_obj.facts:
            fact = random.choice(st.session_state.password_obj.facts)
            st.success(f"📘 Fact: {fact}")

    # --- Win Screen ---
    elif st.session_state.game_state == "won":
        st.balloons()
        st.success("🎉 You guessed the password correctly!")
        st.button("Play Again", on_click=reset_game)

    # --- Failed Screen ---
    elif st.session_state.game_state == "failed":
        st.error("❌ You failed to guess the password.")
        st.info(f"The password was: **{st.session_state.password_obj.password}**")
        st.button("Play Again", on_click=reset_game)
