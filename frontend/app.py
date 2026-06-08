import streamlit as st
import requests
import pyrebase
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.chat-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #FF4B4B;
}

.user-message {
    background-color: #262730;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    color: white;
    text-align: right;
}

.bot-message {
    background-color: #1E1E1E;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# API URL
# =========================================================

#API_URL = "http://127.0.0.1:8000/chat"
API_URL = "https://backend-firebasechat-5.onrender.com/chat"

# =========================================================
# FIREBASE CONFIG
# =========================================================

firebaseConfig = {
    "apiKey": "AIzaSyBSNM1aKnvYyqR0jbe6vfSnMMdATu0QlgQ",
    "authDomain": "chatbot-ecf27.firebaseapp.com",
    "projectId": "chatbot-ecf27",
    "storageBucket": "chatbot-ecf27.firebasestorage.app",
    "messagingSenderId": "350942830968",
    "appId": "1:350942830968:web:3840df0ef5ca53a6cfa88d",
    "measurementId": "G-PTB09B6403",
    "databaseURL": "https://chatbot-ecf27-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

# =========================================================
# FIREBASE INIT
# =========================================================

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# =========================================================
# SESSION
# =========================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<p class="chat-title">🔥 AI Chatbot</p>',
    unsafe_allow_html=True
)

# =========================================================
# LOGIN / SIGNUP
# =========================================================

if st.session_state.token is None:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # =====================================================
    # LOGIN
    # =====================================================

    with tab1:

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            try:

                user = auth.sign_in_with_email_and_password(
                    email,
                    password
                )

                st.session_state.token = user["idToken"]
                st.session_state.user_id = user["localId"]

                st.success("Login Successful")

                st.rerun()

            except Exception:

                st.error("Invalid Email or Password")

    # =====================================================
    # SIGNUP
    # =====================================================

    with tab2:

        signup_email = st.text_input(
            "Signup Email"
        )

        signup_password = st.text_input(
            "Signup Password",
            type="password"
        )

        if st.button("Create Account"):

            try:

                auth.create_user_with_email_and_password(
                    signup_email,
                    signup_password
                )

                st.success("Account Created")

            except Exception as e:

                st.error("Signup Failed")
                st.write(e)

# =========================================================
# CHAT UI
# =========================================================

else:

    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.success("Logged In")

        st.code(st.session_state.user_id)

        if st.button("Logout"):

            st.session_state.token = None
            st.session_state.user_id = None
            st.session_state.messages = []

            st.rerun()

    # =====================================================
    # CHAT HISTORY
    # =====================================================

    for msg in st.session_state.messages:

        if msg["role"] == "user":

            st.markdown(
                f"""
                <div class="user-message">
                🧑 {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="bot-message">
                🤖 {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================
    # INPUT
    # =====================================================

    prompt = st.chat_input("Type your message")

    # =====================================================
    # SEND MESSAGE
    # =====================================================

    if prompt:

        # save user message

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        headers = {
            "authorization": f"Bearer {st.session_state.token}"
        }

        payload = {
            "message": prompt,
            "user_id": st.session_state.user_id
        }

        try:

            with st.spinner("Thinking..."):

                response = requests.post(
                    API_URL,
                    json=payload,
                    headers=headers,
                    timeout=60
                )

                # convert json

                
                try:
                    data = response.json()
                except Exception:

                    st.error("Backend did not return JSON")
                    st.write(response.text)
                    st.stop()

                # only response content

                ai_response = data["response"]

                # streaming effect

                placeholder = st.empty()

                full_response = ""

                for word in ai_response.split():

                    full_response += word + " "

                    placeholder.markdown(
                        f"""
                        <div class="bot-message">
                        🤖 {full_response}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    time.sleep(0.03)

                # save ai message

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })

                st.rerun()

        except Exception as e:

            st.error("API Error")
            st.write(e)