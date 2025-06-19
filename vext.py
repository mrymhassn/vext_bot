import streamlit as st
import requests

# ---- Initialize session state for keys ----
for var in ["VEXT_API_KEY", "CHANNEL_TOKEN", "ENDPOINT_ID"]:
    if var not in st.session_state:
        st.session_state[var] = ""

# ---- Sidebar for Environment Variables ----
st.sidebar.header("🔐 VextApp Credentials")

st.session_state["VEXT_API_KEY"] = st.sidebar.text_input("API Key", type="password")
st.session_state["CHANNEL_TOKEN"] = st.sidebar.text_input("Channel Token")
st.session_state["ENDPOINT_ID"] = st.sidebar.text_input("Endpoint ID")

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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat Input at Bottom ----
user_message = st.chat_input("Ask your question...")

if user_message:
    # Append user's message
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Call VextApp API
    with st.spinner("Contacting VextApp..."):
        response = invoke_vextapp(user_message)

    # Handle response
    if "error" in response:
        bot_reply = f"❌ Error: {response['error']}"
        if response.get("details"):
            bot_reply += f"\n\n```\n{response['details']}\n```"
    else:
        # If the API response is a dict, convert to string or extract relevant part
        bot_reply = response.get("response") or str(response)

    # Append bot's message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

