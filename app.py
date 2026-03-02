import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables if any
load_dotenv()

# Set Page Config
st.set_page_config(
    page_title="AI Multi-Tool Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for "Premium" look
st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Modern Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Light Sidebar with Black Text */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Target all text in sidebar to be black */
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: #1a1a1a !important;
    }

    /* Radio button labels specifically */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }

    /* Glassmorphism Containers */
    .glass-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }

    .glass-container:hover {
        transform: translateY(-5px);
        border-color: #38bdf8;
    }

    /* Header Styling */
    h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.8rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.8rem !important;
    }

    h2, h3 {
        color: #e2e8f0;
        font-weight: 600;
    }

    /* Custom Input Boxes */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(15, 23, 42, 0.8) !important; /* Darker, solid-ish background */
        color: #ffffff !important; /* Pure white text for max contrast */
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.3) !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
    }

    /* Target Placeholder Text */
    ::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
        opacity: 1;
    }

    /* Chat Input Styling - Light background with Black Text */
    [data-testid="stChatInput"] {
        background-color: #f1f5f9 !important; /* Light background */
        border: 1px solid #cbd5e1 !important;
        border-radius: 16px !important;
        color: #1e293b !important; /* Black/Dark text */
    }

    [data-testid="stChatInput"] textarea {
        color: #1e293b !important; /* Black/Dark text */
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] button {
        background-color: #38bdf8 !important;
        color: white !important;
        border-radius: 50% !important;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
    }

    .stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
    }

    /* High Contrast Rules for Main Area */
    .stApp, [data-testid="stChatMessage"], [data-testid="stChatMessageContent"] p {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff !important;
    }

    /* Ensure chat bubble content specifically is white */
    .stChatMessage div {
        color: #ffffff !important;
    }

    /* If background is light (like inside some Streamlit alerts or inputs), text is black */
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        color: #1a1a1a !important; /* Very dark text for readability on lighter alerts */
    }
    
    .stAlert p, .stInfo p, .stSuccess p, .stWarning p, .stError p {
        color: #1a1a1a !important;
    }

    /* Specific Input Contrast */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.8s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)

# Helper Function: LLM Interaction with Fallback Model
def call_gemini(prompt, api_key):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
        return None
    
    # Models to try in order (based on verified availability)
    models_to_try = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-pro-latest"]
    
    last_error = ""
    for model_name in models_to_try:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            # If it's a quota error or model not found, try the next one
            if "429" in error_msg or "404" in error_msg or "Quota exceeded" in error_msg:
                continue
            else:
                st.error(f"Error with {model_name}: {error_msg}")
                return None
    
    # If all models failed
    if "429" in last_error or "Quota exceeded" in last_error:
        st.warning("⚠️ API Quota Exceeded. The free tier of Gemini has limited requests. Please wait a moment and try again, or check your API key's billing details.")
    else:
        st.error(f"All models failed. Last error: {last_error}")
    return None

# Sidebar Configuration
with st.sidebar:
    st.markdown("<h1 style='font-size: 1.2rem !important; font-weight: 800; margin-bottom: 0rem; white-space: nowrap;'>Multi-Tool AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.8rem; margin-bottom: 2rem;'>Advanced AI Assistant</p>", unsafe_allow_html=True)
    
    st.subheader("Settings")
    
    # Try to load API key from environment variable
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Gemini API Key", 
        value=env_key, 
        type="password", 
        help="Get yours at aistudio.google.com"
    )
    
    st.markdown("---")
    st.header("Tools")
    selection = st.radio("Choose a Tool", ["Text Summarizer", "Idea Generator", "AI Chatbot"])
    
    st.markdown("---")
    st.info("💡 Pro Tip: Be specific in your prompts for better results.")

# Main Application Logic
st.markdown("<div class='animate-in'>", unsafe_allow_html=True)

if selection == "Text Summarizer":
    st.title("📄 Text Summarizer")
    st.write("Transform long articles into concise, actionable summaries.")
    
    with st.container():
        text_input = st.text_area("Paste your text here...", height=300)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Summarize Now"):
                if text_input:
                    with st.spinner("Analyzing and condensing..."):
                        prompt = f"Summarize the following text clearly and concisely, focusing on the key points: \n\n{text_input}"
                        summary = call_gemini(prompt, api_key)
                        if summary:
                            st.markdown("### Summary")
                            st.write(summary)
                            st.success("Summary Generated!")
                else:
                    st.warning("Please paste some text first.")

elif selection == "Idea Generator":
    st.title("💡 Idea Generator")
    st.write("Fuel your creativity with AI-powered brainstorming.")
    
    with st.container():
        topic = st.text_input("What's the topic or theme?", placeholder="e.g., Sustainable Packaging, Sci-Fi Novel, YouTube Channel")
        
        num_ideas = st.slider("How many ideas?", 5, 20, 10)
        
        if st.button("Spark Ideas"):
            if topic:
                with st.spinner(f"Brainstorming {num_ideas} ideas for {topic}..."):
                    prompt = f"Generate {num_ideas} creative and unique ideas for the topic: '{topic}'. Format them as a list with brief descriptions for each."
                    ideas = call_gemini(prompt, api_key)
                    if ideas:
                        st.markdown(f"### Creative Ideas for: {topic}")
                        st.write(ideas)
            else:
                st.warning("Please enter a topic.")

elif selection == "AI Chatbot":
    st.title("🤖 AI Chatbot")
    st.write("Chat with an intelligent assistant to solve problems or learn something new.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if api_key:
                with st.spinner("Thinking..."):
                    # Construct conversation history for the prompt
                    history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
                    full_prompt = f"You are a helpful and intelligent AI assistant. Conversation history:\n{history}\nassistant:"
                    response = call_gemini(full_prompt, api_key)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("Please provide an API key in the sidebar.")

st.markdown("</div>", unsafe_allow_html=True)
