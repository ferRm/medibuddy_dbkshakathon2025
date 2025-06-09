import logging
import os
import streamlit as st
from model_serving_utils import query_endpoint

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure environment variable is set correctly
assert os.getenv('SERVING_ENDPOINT'), "SERVING_ENDPOINT must be set in app.yaml."

def get_user_info():
    headers = st.context.headers
    return dict(
        user_name=headers.get("X-Forwarded-Preferred-Username"),
        user_email=headers.get("X-Forwarded-Email"),
        user_id=headers.get("X-Forwarded-User"),
    )

user_info = get_user_info()

# Streamlit app
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

st.title("MediBuddy")
st.markdown(
    "ℹ️ MediBuddy is an AI assitant to help you understand complex medical terminology in simple, everyday language. It is designed to provide accurate and helpful information to patients and healthcare providers. It is not intended to replace medical professionals or provide medical advice. If you have any concerns or questions about your health, please consult with a qualified healthcare professional."
)

# Set background image
page_bg_img = '''
<style>
.stApp {
  background-image: url("https://dbc-8eded093-9f6c.cloud.databricks.com/editor/files/3486519396198887?o=467110276845047");
  background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Upload document feature
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt", "docx"])
if uploaded_file:
    file_content = uploaded_file.read()
    st.session_state.messages.append({"role": "system", "content": f"User uploaded document: {uploaded_file.name}"})
    # Optionally, you can add the file content to messages or process it as needed

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Left navigation panel to view the last 5 prompts
with st.sidebar:
    st.header("Chat History")
    last_5_prompts = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"][-5:]
    for i, prompt in enumerate(last_5_prompts, 1):
        st.write(f"{i}. {prompt}")

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.image("images/istockphoto-1139549801-612x612.jpg", width=50)  # Add image for the chat bot
        # Query the Databricks serving endpoint
        assistant_response = query_endpoint(
            endpoint_name=os.getenv("SERVING_ENDPOINT"),
            messages=st.session_state.messages,
            max_tokens=400,
        )["content"]
        st.markdown(assistant_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})