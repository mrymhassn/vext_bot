import streamlit as st
import requests#
from uuid import uuid4

random_id = str(uuid4().hex[:10])
# ---- Initialize session state for keys ----
for var in ["VEXT_API_KEY", "CHANNEL_TOKEN", "ENDPOINT_ID"]:
    if var not in st.session_state:
        st.session_state[var] = ""

# ---- Sidebar for Environment Variables ----
st.sidebar.header("🔐 VextApp Credentials")

st.session_state["VEXT_API_KEY"] = st.secrets['VEXT_API_KEY']
st.session_state["CHANNEL_TOKEN"] = random_id
st.session_state["ENDPOINT_ID"] = st.secrets['ENDPOINT_ID']

# ---- Initialize message history ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- API Call Function (uses session_state) ----
def invoke_vextapp(message: str, env: str = "dev") -> dict:
    api_token = st.session_state.get("VEXT_API_KEY")
    channel_token = st.session_state.get("CHANNEL_TOKEN")
    endpoint_id = st.session_state.get("ENDPOINT_ID")

    if not api_token or not channel_token or not endpoint_id:
        return {"error": "Missing API credentials. Please fill in all fields in the sidebar."}

    url = f"https://payload.vextapp.com/hook/{endpoint_id}/catch/{channel_token}"
    headers = {
        "Content-Type": "application/json",
        "Apikey": f"Api-Key {api_token}"
    }

    payload = {
        "payload": message,
        "env": env
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "details": getattr(e.response, "text", None)
        }

# ---- Display Chat Messages ----
st.title("🧠 VextApp Q&A Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat Input at Bottom ----
user_message = st.chat_input("Ask your question...")

if user_message:
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_message)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Call VextApp API and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = invoke_vextapp(user_message)
        
        # Handle response
        if "error" in response:
            bot_reply = f"❌ Error: {response['error']}"
            if response.get("details"):
                bot_reply += f"\n\n```\n{response['details']}\n```"
        else:
            # Extract the actual response from the API
            bot_reply = response.get("response") or response.get("message") or response.get("text")
            
        # Display the response
        st.markdown(bot_reply)
    
    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# ---- Optional: Clear Chat Button ----
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

    