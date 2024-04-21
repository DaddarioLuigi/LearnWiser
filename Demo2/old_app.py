from openai import OpenAI
import openai
from typing_extensions import override
from openai import AssistantEventHandler
import streamlit as st
import json
import re


# Initialization: Set up the OpenAI API and create resources
def init_openai_client():
    openai.api_key = "sk-proj-5qtr7opslFoSsTvmbN3hT3BlbkFJY4mFDMG95nNEEdD378rR"
    client = OpenAI(api_key=openai.api_key)

    # Create an assistant
    assistant = client.beta.assistants.create(
        name="Math Tutor",
        instructions="You are a helpful math tutor. Generate exercises based on uploaded STEM PDFs.",
        tools=[{"type": "file_search"}],
        model="gpt-4-turbo",
    )

    # Create a vector store
    vector_store = client.beta.vector_stores.create(name="Math Exercises")

    return client, assistant, vector_store


client, assistant, vector_store = init_openai_client()


# Streamlit App
def main():
    st.title("Math Exercise Generator")

    # File upload
    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
    if uploaded_file is not None:
        # Upload file and poll for completion
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_stream = open(uploaded_file.name, "rb")

        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=[file_stream]
        )

        if file_batch.status == "completed":
            st.success("File uploaded successfully!")

            # Send a user message to the assistant
            thread = client.beta.threads.create()
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Write a single multiple choice exercise on the topic of Interests.Generate as a json of scheme to be the argument of a function: {question: string, right_answer: string, wrong_answer_1:string, wrong_answer_2:string, wrong_answer_3:string, right_answer_explanation: string}. Use only json, do not use natural language",
            )

            # Create and poll a run
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id, assistant_id=assistant.id
            )

            # Retrieve generated exercise
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

            # Display the exercise
            # st.write(message_content.value)
            print(message_content.value)
            json_output = re.search(r"\{.*\}", message_content.value, re.DOTALL)
            print(json_output.group(0))
            exercise = json.loads(json_output.group(0))
            # Display parsed content
            st.subheader("Question")
            st.write(exercise["question"])

            st.subheader("Options")
            # Create buttons for each answer option
            if "selected_answer" not in st.session_state:
                st.session_state.selected_answer = None
                st.session_state.correct = None

            # Helper function to handle button press logic
            def handle_answer(answer, correct_answer):
                st.session_state.selected_answer = answer
                st.session_state.correct = answer == correct_answer

            # Display buttons with answers
            if st.button(f"A: {exercise['right_answer']}"):
                handle_answer(exercise["right_answer"], exercise["right_answer"])
            if st.button(f"B: {exercise['wrong_answer_1']}"):
                handle_answer(exercise["wrong_answer_1"], exercise["right_answer"])
            if st.button(f"C: {exercise['wrong_answer_2']}"):
                handle_answer(exercise["wrong_answer_2"], exercise["right_answer"])
            if st.button(f"D: {exercise['wrong_answer_3']}"):
                handle_answer(exercise["wrong_answer_3"], exercise["right_answer"])

            # Feedback and explanation
            if st.session_state.selected_answer is not None:
                if st.session_state.correct:
                    st.success("Correct!")
                    st.subheader("Explanation for the Right Answer")
                    st.write(exercise["right_answer_explanation"])
                else:
                    st.error("Wrong answer.")
                    st.subheader("Explanation for the Right Answer")
                    st.write(exercise["right_answer_explanation"])

                # Optionally, reset the question for another attempt
                # st.button("Try another question", on_click=lambda: st.session_state.clear())
        else:
            st.error("Failed to upload file.")


if __name__ == "__main__":
    main()
