import streamlit as st
import os
from datetime import date
from rag_pipeline import initialize_pipeline

st.set_page_config(
    page_title="Personal Productivity Coach",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Personal Productivity Coach")
st.caption("Log your daily habits and get personalised suggestions based on YOUR data.")

# ── Two tabs ──
tab1, tab2 = st.tabs(["📝 Log Today", "💬 Chat"])

# ── TAB 1: Daily Log Form ──
with tab1:
    st.subheader("How was your day?")

    with st.form("daily_log"):
        log_date = st.date_input("Date", value=date.today())

        screen_time = st.slider(
            "Total Screen Time (hours)",
            min_value=0.0, max_value=16.0, step=0.5, value=4.0
        )

        apps = st.text_input(
            "Most Used Apps",
            placeholder="e.g. Instagram (1hr), YouTube (30mins), WhatsApp (45mins)"
        )

        sleep = st.slider(
            "Sleep Last Night (hours)",
            min_value=0.0, max_value=12.0, step=0.5, value=7.0
        )

        exercise = st.selectbox(
            "Did you exercise?",
            ["No", "Yes - 15 mins", "Yes - 30 mins", "Yes - 45 mins", "Yes - 1 hour+"]
        )

        mood = st.select_slider(
            "Mood Today",
            options=["Terrible", "Anxious", "Tired", "Average", "Good", "Excellent"]
        )

        productivity = st.slider(
            "Productivity Score",
            min_value=1, max_value=10, value=5
        )

        notes = st.text_area(
            "Notes — what went well and what didn't? (required for better suggestions)",
            placeholder="e.g. Instagram was mindless scrolling. Teams was productive work. Felt tired by 3pm...",
            height=100
        )

        submitted = st.form_submit_button("💾 Save Today's Log")

    if submitted:
        # Validate notes
        if not notes.strip():
            st.error("⚠️ Please add notes for better personalised suggestions!")
            st.stop()

        # Validate apps
        if not apps.strip():
            st.error("⚠️ Please add your most used apps!")
            st.stop()

        # Format the log entry
        log_entry = f"""
Date: {log_date}
Screen Time: {screen_time} hours
Most Used Apps: {apps}
Sleep: {sleep} hours
Exercise: {exercise}
Mood: {mood}
Productivity Score: {productivity}/10
Notes: {notes}

"""
        # Append to logs.txt
        with open("data/logs.txt", "a") as f:
            f.write(log_entry)

        st.success(f"✅ Log saved for {log_date}!")
        st.info("Go to the Chat tab to ask questions about your habits.")

        # Clear cache so pipeline reloads with new data
        st.cache_resource.clear()

    # Show existing logs
    st.divider()
    st.subheader("📋 Your Previous Logs")

    if os.path.exists("data/logs.txt") and os.path.getsize("data/logs.txt") > 0:
        with open("data/logs.txt", "r") as f:
            content = f.read().strip()
        if content:
            st.text(content)
        else:
            st.info("No logs yet. Fill the form above to get started!")
    else:
        st.info("No logs yet. Fill the form above to get started!")

# ── TAB 2: Chat ──
with tab2:
    st.subheader("Ask me about your habits")

    # Check if logs exist and have content
    has_data = (
        os.path.exists("data/logs.txt") and
        os.path.getsize("data/logs.txt") > 10
    )

    if not has_data:
        st.warning("⚠️ No data yet! Go to 'Log Today' tab and add at least one day first.")
    else:
        # Load pipeline
        @st.cache_resource
        def load_pipeline():
            return initialize_pipeline()

        with st.spinner("Loading your productivity data..."):
            rag_chain = load_pipeline()

        st.success("✅ Ready! Ask me anything about your habits.")

        # Show how many days logged
        with open("data/logs.txt", "r") as f:
            content = f.read()
        days_logged = content.count("Date:")
        st.caption(f"📊 Based on {days_logged} day(s) of your data")

        # Suggested questions
        st.markdown("**Try asking:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📱 Which apps waste my time?"):
                st.session_state.suggested = "Which apps am I spending too much time on?"
        with col2:
            if st.button("😴 How does sleep affect me?"):
                st.session_state.suggested = "How does my sleep affect my productivity?"

        col3, col4 = st.columns(2)
        with col3:
            if st.button("🏆 What was my best day?"):
                st.session_state.suggested = "What was my best day and why?"
        with col4:
            if st.button("📈 How can I improve?"):
                st.session_state.suggested = "What should I do to improve my productivity?"

        st.divider()

        # Chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Show previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Handle suggested question
        if "suggested" in st.session_state:
            question = st.session_state.suggested
            del st.session_state.suggested

            with st.chat_message("user"):
                st.write(question)
            st.session_state.messages.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                with st.spinner("Analysing your habits..."):
                    answer = rag_chain.invoke(question)
                st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        # Chat input
        if question := st.chat_input("Ask about your productivity habits..."):
            with st.chat_message("user"):
                st.write(question)
            st.session_state.messages.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                with st.spinner("Analysing your habits..."):
                    answer = rag_chain.invoke(question)
                st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})