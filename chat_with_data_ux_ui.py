# -*- coding: utf-8 -*-
"""chat with data UX UI.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1x4614rb8KlQ9_JyYeufQq1a4NK-VeDf_
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
import traceback
import time
from datetime import datetime

# Set page configuration with dark theme
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and modern AI feel
st.markdown("""
<style>
    /* Main page background and text */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }

    /* Headers */
    h1, h2, h3 {
        color: #00CCFF !important;
        font-family: 'Arial', sans-serif;
    }

    /* Title styling with glow effect */
    .title-container {
        background: linear-gradient(90deg, #0E1117, #1A1C24, #0E1117);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
    }

    .ai-title {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-shadow: 0 0 10px rgba(0, 204, 255, 0.7);
    }

    /* Card containers */
    .card {
        background-color: #1A1C24;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 3px solid #00CCFF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* File upload area */
    .stFileUploader {
        padding: 10px;
        border-radius: 8px !important;
        background-color: #252a33 !important;
    }

    /* Success messages */
    .success-message {
        background-color: rgba(0, 128, 0, 0.2);
        color: #00FF00;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }

    /* Chat message styling */
    .chat-container {
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        background-color: #1A1C24;
        border: 1px solid #2D3748;
    }

    .user-message {
        background-color: #2D3748;
        border-radius: 15px 15px 0 15px;
        padding: 10px 15px;
        margin: 5px 0;
        color: white;
        text-align: right;
        display: inline-block;
        float: right;
        max-width: 80%;
        clear: both;
    }

    .bot-message {
        background-color: #3700B3;
        border-radius: 15px 15px 15px 0;
        padding: 10px 15px;
        margin: 5px 0;
        color: white;
        text-align: left;
        display: inline-block;
        float: left;
        max-width: 80%;
        clear: both;
    }

    /* Chat input box */
    .stTextInput > div > div > input {
        background-color: #252a33 !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        border: 1px solid #3700B3 !important;
    }

    /* Tables/DataFrames */
    .dataframe {
        background-color: #1A1C24 !important;
    }

    /* Pulsing animation for AI processing */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .ai-processing {
        animation: pulse 1.5s infinite;
        color: #00CCFF;
        text-align: center;
        padding: 10px;
    }

    /* Loading bar */
    .loading-bar {
        height: 3px;
        width: 100%;
        background: linear-gradient(90deg, #3700B3, #00CCFF);
        position: relative;
        overflow: hidden;
        border-radius: 2px;
    }
    .loading-bar::before {
        content: "";
        position: absolute;
        height: 100%;
        width: 50%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.7), transparent);
        animation: loading 1.5s infinite;
    }
    @keyframes loading {
        0% { left: -50%; }
        100% { left: 100%; }
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #161A22 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #3700B3 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 8px 16px !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background-color: #651FFF !important;
        box-shadow: 0 0 10px rgba(101, 31, 255, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# Gemini API Setup
@st.cache_resource
def setup_api():
    try:
        key = st.secrets['gemini_api_key']
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        return model, True
    except Exception as e:
        st.error(f"Failed to configure Gemini API: {e}")
        return None, False

model, api_configured = setup_api()

# Custom title with AI feel
st.markdown("""
<div class="title-container">
    <h1 class="ai-title">🤖 AI Data Analyst</h1>
    <p style="color: #00CCFF; margin-top: 5px;">Powered by Gemini AI</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = []
if "data_context" not in st.session_state:
    st.session_state.data_context = ""
if "data_dictionary" not in st.session_state:
    st.session_state.data_dictionary = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# Create sidebar for data upload and settings
with st.sidebar:
    st.markdown("<h3 style='color: #00CCFF;'>📊 Data Management</h3>", unsafe_allow_html=True)

    # Create nice card for file upload
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00CCFF;'>Upload CSV Files</h4>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Choose one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="Upload your CSV datasets for analysis"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Dictionary upload card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00CCFF;'>Data Dictionary</h4>", unsafe_allow_html=True)

    dict_file = st.file_uploader(
        "Upload a CSV data dictionary file",
        type=["csv"],
        help="Optional: Upload a data dictionary to provide context for your columns"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Display file status
    if st.session_state.uploaded_data:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #00CCFF;'>Loaded Files</h4>", unsafe_allow_html=True)

        for idx, (file_name, _) in enumerate(st.session_state.uploaded_data):
            is_active = st.session_state.current_file == idx
            file_status = "✓ " if is_active else ""
            if st.button(f"{file_status}{file_name}", key=f"file_{idx}"):
                st.session_state.current_file = idx
                st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # About section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00CCFF;'>About</h4>", unsafe_allow_html=True)
    st.markdown("""
    This AI Data Analyst uses Gemini AI to analyze your CSV datasets.
    Upload your files, then chat with the AI to get insights about your data.
    """)
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"<p style='color: #888; font-size: 0.8rem;'>Current time: {current_time}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

# Process uploaded files
if uploaded_files:
    all_contexts = []
    new_files = []

    for file in uploaded_files:
        # Check if file is already loaded
        if not any(file.name == f[0] for f in st.session_state.uploaded_data):
            try:
                df = pd.read_csv(file)
                new_files.append((file.name, df))

                # Create data context for AI
                description = df.describe(include='all').to_string()
                sample_rows = df.head(3).to_string(index=False)
                columns_info = "\n".join([f"- {col}: {dtype}" for col, dtype in zip(df.columns, df.dtypes)])
                file_context = (
                    f"File: {file.name}\n"
                    f"Columns and Types:\n{columns_info}\n\n"
                    f"Descriptive Statistics:\n{description}\n\n"
                    f"Sample Records:\n{sample_rows}\n"
                )
                all_contexts.append(file_context)

                with col1:
                    st.markdown(f"""
                    <div class='success-message'>
                        ✅ File '{file.name}' successfully loaded
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                with col1:
                    st.error(f"Error loading '{file.name}': {e}")

    # Update session state with new files
    if new_files:
        st.session_state.uploaded_data.extend(new_files)
        if st.session_state.current_file is None and st.session_state.uploaded_data:
            st.session_state.current_file = 0

        # Update data context
        existing_context = st.session_state.data_context if st.session_state.data_context else "You are a helpful data analyst AI. The user uploaded multiple datasets. Here is the context for each:\n\n"
        st.session_state.data_context = existing_context + "\n\n".join(all_contexts)

# Process data dictionary
if dict_file is not None:
    try:
        data_dict = pd.read_csv(dict_file)
        st.session_state.data_dictionary = data_dict
        dict_info = data_dict.to_string(index=False)
        st.session_state.data_context += f"\n\nData Dictionary:\n{dict_info}"

        with col1:
            st.markdown("""
            <div class='success-message'>
                ✅ Data dictionary successfully loaded
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        with col1:
            st.error(f"Error loading data dictionary: {e}")

# Display current dataset preview
with col1:
    if st.session_state.uploaded_data and st.session_state.current_file is not None:
        current_filename, current_df = st.session_state.uploaded_data[st.session_state.current_file]

        st.markdown(f"""
        <div class='card'>
            <h3 style='color: #00CCFF;'>Dataset Preview: {current_filename}</h3>
        </div>
        """, unsafe_allow_html=True)

        # Data summary card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Rows", f"{current_df.shape[0]:,}")
        with col_stats2:
            st.metric("Columns", current_df.shape[1])
        with col_stats3:
            memory_usage = current_df.memory_usage(deep=True).sum()
            memory_unit = "KB"
            if memory_usage > 1024**2:
                memory_usage = memory_usage / (1024**2)
                memory_unit = "MB"
            elif memory_usage > 1024:
                memory_usage = memory_usage / 1024
                memory_unit = "KB"
            st.metric("Memory Usage", f"{memory_usage:.2f} {memory_unit}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Data preview
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #00CCFF;'>Data Preview</h4>", unsafe_allow_html=True)
        st.dataframe(current_df.head(5), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Data dictionary preview if available
        if st.session_state.data_dictionary is not None:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00CCFF;'>Data Dictionary</h4>", unsafe_allow_html=True)
            st.dataframe(st.session_state.data_dictionary, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Chat interface
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #00CCFF;'>💬 AI Data Assistant</h3>", unsafe_allow_html=True)

    # Display welcome message if chat history is empty
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="padding: 15px; border-radius: 10px; background-color: #252a33; margin-bottom: 20px;">
            <p style="margin: 0; color: #00CCFF;"><strong>👋 Welcome to AI Data Analyst!</strong></p>
            <p>Upload your CSV files and ask me questions about your data. I can help with:</p>
            <ul>
                <li>Data analysis and statistics</li>
                <li>Visualizations and trends</li>
                <li>Finding insights in your data</li>
                <li>Answering specific questions about your dataset</li>
            </ul>
            <p style="margin: 0; font-style: italic; color: #888;">Example: "What's the average age in the dataset?" or "Show me the distribution of sales by region"</p>
        </div>
        """, unsafe_allow_html=True)

    # Chat message container
    chat_container = st.container()
    with chat_container:
        for i, (role, message) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px; clear: both;">
                    <div class="user-message">
                        <p style="margin: 0;">{message}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px; clear: both;">
                    <div class="bot-message">
                        <p style="margin: 0;">{message}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Processing indicator
    if st.session_state.processing:
        st.markdown("""
        <div class="ai-processing">
            <p>AI is analyzing your data...</p>
            <div class="loading-bar"></div>
        </div>
        """, unsafe_allow_html=True)

    # Input form
    user_input = st.text_input(
        "พิมพ์คำถามที่ต้องการได้เลยครับ",
        key="chat_input",
        disabled=not api_configured or not st.session_state.uploaded_data,
        placeholder="Ask about your data..."
    )

    if not api_configured:
        st.warning("⚠️ Please configure the Gemini API Key in your Streamlit secrets to enable chat responses.")
    elif not st.session_state.uploaded_data:
        st.info("📤 Please upload data files to begin analysis")

    st.markdown("</div>", unsafe_allow_html=True)

# Handle user input & AI response
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.processing = True
    st.experimental_rerun()

# Process the response (This will run after the rerun if there's pending input)
if st.session_state.processing and st.session_state.uploaded_data:
    for file_index, (file_name, df) in enumerate(st.session_state.uploaded_data):
        if st.session_state.current_file is not None and file_index != st.session_state.current_file:
            continue

        df_name = "df"
        example_record = df.head(2).to_string(index=False)
        data_dict_text = "\n".join([f"{col}: {dtype}" for col, dtype in zip(df.columns, df.dtypes)])
        question = st.session_state.chat_history[-1][1]  # Get the last user question

        # Prompt for code generation
        code_prompt = f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question and the provided DataFrame information.
Here's the context:
**User Question:**
{question}
**DataFrame Name:**
{df_name}
**DataFrame Details:**
{data_dict_text}
**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. **Use the `exec()` function to execute the generated code.**
3. Do not import pandas, but you may assume `pd` (pandas) is already available.
4. Change date column type to datetime if needed.
5. Store the result in a variable named `ANSWER`.
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`.
7. Keep the generated code concise and focused on answering the question.
8. If the question requires a specific output format (e.g., a list, a single value), ensure the `ANSWER` variable holds that format.
"""

        try:
            response = model.generate_content(code_prompt)
            generated_code = response.text

            # Clean the code and execute it
            cleaned_code = generated_code.strip().replace("```python", "").replace("```", "")
            local_vars = {df_name: df.copy(), "pd": pd}
            exec(cleaned_code, {}, local_vars)

            # Check if ANSWER variable exists in the local variables
            if "ANSWER" not in local_vars:
                answer_result = "No result in variable ANSWER"
            else:
                answer_result = local_vars["ANSWER"]

            # Display result based on type
            if isinstance(answer_result, pd.DataFrame):
                result_preview = f"DataFrame with {len(answer_result)} rows and {len(answer_result.columns)} columns"
            else:
                result_preview = str(answer_result)

            # Add result to chat history
            st.session_state.chat_history.append(("assistant", f"**Analysis Result:**\n{result_preview}"))

            # Prompt for explanation
            explain_prompt = f'''
The user asked: "{question}"
Here is the result:\n{str(answer_result)}
Answer the question and summarize the findings in a clear, concise way.
Include your opinion of the persona of this customer if relevant.
Format your response with markdown for readability.
'''
            explain_response = model.generate_content(explain_prompt)
            explanation_text = explain_response.text
            st.session_state.chat_history.append(("assistant", explanation_text))

            # Display analysis result in the right column
            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color: #00CCFF;'>🔍 Analysis Result</h3>", unsafe_allow_html=True)

                if isinstance(answer_result, pd.DataFrame):
                    st.dataframe(answer_result.head(10), use_container_width=True)

                    if len(answer_result) > 10:
                        st.info(f"Showing 10 of {len(answer_result)} total rows")

                else:
                    st.markdown(f"```\n{answer_result}\n```")

                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            error_msg = f"⚠️ An error occurred: {str(e)}"
            st.session_state.chat_history.append(("assistant", error_msg))

    # Reset processing flag
    st.session_state.processing = False
    st.experimental_rerun()

# Add a footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 20px; color: #888;">
    <p style="font-size: 0.8rem;">© 2025 AI Data Analyst | Built with Streamlit and Gemini AI</p>
</div>
""", unsafe_allow_html=True)