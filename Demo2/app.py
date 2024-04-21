from openai import OpenAI
import openai
import streamlit as st
import json
import re
import time

import streamlit as st

# Set page config
st.set_page_config(
    page_title="LearnWiser",
    layout="centered",
    page_icon=":school:",
    initial_sidebar_state="expanded",
)


# Custom styles
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# local_css("style.css")  # assuming you have a style.css file with your CSS
# def apply_custom_css():
#     st.markdown(
#         """
#         <style>
#         /* Targeting the root container of Streamlit content */
#         .stApp {
#             background-color: #3f3cbb !important; /* Dark purple background */
#         }

#         /* Targeting the main block area for content */
#         .main .block-container {
#             background-color: #3f3cbb !important; /* Dark purple background */
#             color: white !important;
#         }

#         /* Button colors and styles */
#         .stButton > button {
#             background-color: #8a81d6; /* Lighter purple for buttons */
#             color: white;
#             border-radius: 5px;
#             border: none;
#             padding: 10px 20px;
#             margin: 5px 0;
#         }

#         /* Text input and text area */
#         .stTextInput, .stTextArea {
#             color: white;
#         }

#         /* Headers and paragraphs */
#         h1, h2, h3, h4, h5, p {
#             color: white !important;
#         }

#         /* Additional custom styles */
#         /* ... */

#         </style>
#         """,
#         unsafe_allow_html=True,
#     )


# apply_custom_css()
def apply_simple_css():
    st.markdown(
        """
        <style>
        /* MAIN STUFF */
        .main { background: #120c59 url("back.png") no-repeat fixed center !important; }
        st-emotion-cache-10trblm e1nzilvr1, .st-emotion-cache-1629p8f a , h1,.st-emotion-cache-ue6h4q,p{
            color: white !Important;
        }
        
        /* SIDEBAR */
        .st-emotion-cache-6qob1r, .eczjsme3 {
            background-color: #B36DFF !Important;
        }
        
        /* BUTTON */
        .st-emotion-cache-7ym5gk, .ef3psqc12 {
            color: white !Important;
            background-color: #C5EF07 !Important;  
            border: 2px #C5EF07;
        }
        
        .st-emotion-cache-1629p8f span {
            color:white !Important;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_simple_css()


def escape_markdown(text):
    """
    Escape markdown special characters from the text
    """
    markdown_escape = {
        r"\$": r"\$",  # Dollar sign
        r"\*": r"\*",  # Asterisk
        r"\_": r"\_",  # Underscore
        r"\{": r"\{",  # Curly braces
        r"\}": r"\}",
        r"\[": r"\[",  # Square brackets
        r"\]": r"\]",
        r"\(": r"\(",  # Parentheses
        r"\)": r"\)",
        r"\#": r"\#",  # Hash symbol
        r"\+": r"\+",  # Plus sign
        r"\-": r"\-",  # Minus sign (dash)
        r"\!": r"\!",  # Exclamation mark
        r"\.": r"\.",  # Period
    }
    # Replace each special character with its escaped version
    for key, value in markdown_escape.items():
        text = re.sub(key, value, text)
    return text


# Initialization: Set up the OpenAI API and create resources
def init_openai_client(key):
    openai.api_key = key
    client = OpenAI(api_key=openai.api_key)
    assistant = client.beta.assistants.create(
        name="Math Tutor",
        instructions="You are a helpful math tutor. Generate exercises based on uploaded files on STEM subjects.",
        tools=[{"type": "file_search"}],
        model="gpt-4-turbo",
    )
    vector_store = client.beta.vector_stores.create(name="Math Exercises")
    return client, assistant, vector_store


if "api_key" not in st.session_state or st.session_state.api_key == "":
    st.session_state.api_key = st.sidebar.text_input(
        "Enter your OpenAI API Key", type="password"
    )

# Client initialization
if st.session_state.api_key:
    client, assistant, vector_store = init_openai_client(st.session_state.api_key)


@st.cache_data()
def upload_and_process_file(uploaded_file, trigger, topic):
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    file_stream = open(uploaded_file.name, "rb")

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=[file_stream]
    )
    if file_batch.status == "completed":

        print(file_batch.status)
        print(file_batch.file_counts)
        thread = client.beta.threads.create()

        # topic = "Interest and Discount"  # this is hardcoded for demo purposes, but in our application it's passed by the sistem, after the topic parsing phase
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Write a single multiple choice exercise based on {topic}. Generate it as a json of scheme to be the argument of a function: {{question: string, right_answer: string, wrong_answer_1:string, wrong_answer_2:string, wrong_answer_3:string, right_answer_explanation: string}}. Use only json, do not use natural language",
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )
        messages = list(
            client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        )

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")
        print(message_content.value)
        json_output = re.search(r"\{.*\}", message_content.value, re.DOTALL)
        print(json_output.group(0))

        return json.loads(json_output.group(0))
    else:
        return None


def regenerate_question(topic):
    if "uploaded_file" in st.session_state:
        st.session_state.selected_answer = None
        st.session_state.correct = None
        trigger = st.session_state.get("trigger", 0)
        st.session_state.trigger = trigger + 1  # Update the trigger
        st.session_state.exercise = upload_and_process_file(
            st.session_state.uploaded_file, trigger, topic
        )


def main():
    st.title("Math Exercise Generator")

    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
    topic = st.text_input("Enter the topic for the exercises")

    if uploaded_file and topic:
        st.session_state.uploaded_file = uploaded_file
        trigger = st.session_state.get("trigger", 0)

        if "exercise" not in st.session_state:
            st.session_state.trigger = (
                trigger + 1
            )  # Update the trigger, this is done only to avoid caching
            exercise = upload_and_process_file(uploaded_file, trigger, topic)

            if exercise:
                st.session_state.exercise = exercise
                st.success("File uploaded and processed successfully!")
            else:
                st.error("Failed to upload or process file.")

        if "exercise" in st.session_state:
            st.subheader("Question")
            st.write(st.session_state.exercise["question"])

            st.subheader("Options")
            if "selected_answer" not in st.session_state:
                st.session_state.selected_answer = None
                st.session_state.correct = None

            def handle_answer(answer):
                st.session_state.selected_answer = answer
                st.session_state.correct = (
                    answer == st.session_state.exercise["right_answer"]
                )

            if st.button(f"A: {st.session_state.exercise['right_answer']}"):
                handle_answer(st.session_state.exercise["right_answer"])
            if st.button(f"B: {st.session_state.exercise['wrong_answer_1']}"):
                handle_answer(st.session_state.exercise["wrong_answer_1"])
            if st.button(f"C: {st.session_state.exercise['wrong_answer_2']}"):
                handle_answer(st.session_state.exercise["wrong_answer_2"])
            if st.button(f"D: {st.session_state.exercise['wrong_answer_3']}"):
                handle_answer(st.session_state.exercise["wrong_answer_3"])

            if st.session_state.selected_answer is not None:
                if st.session_state.correct:
                    st.success("Correct!")
                else:
                    st.error("Wrong answer.")
                st.subheader("Let me explain")
                answer = escape_markdown(
                    st.session_state.exercise["right_answer_explanation"]
                )
                st.write(answer)

            # Regenerate question button
            st.button(
                "Regenerate Question", on_click=lambda: regenerate_question(topic)
            )


if __name__ == "__main__":
    main()
