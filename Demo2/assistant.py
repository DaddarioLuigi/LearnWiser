from openai import OpenAI
import openai
from typing_extensions import override
from openai import AssistantEventHandler

openai.api_key = "sk-proj-5qtr7opslFoSsTvmbN3hT3BlbkFJY4mFDMG95nNEEdD378rR"

client = OpenAI(api_key="sk-proj-5qtr7opslFoSsTvmbN3hT3BlbkFJY4mFDMG95nNEEdD378rR")


assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a helpful math tutor. As the user gives you text and PDF about STEM subjects, you generate exercises, and you're able to showcase the right solutions. You always try to call function to create and solve the exercises. ",
    tools=[{"type": "file_search"}],
    model="gpt-4-turbo",
)

# Create a vector store caled "Financial Statements"
vector_store = client.beta.vector_stores.create(name="Financial Statements")

# Ready the files for upload to OpenAI
file_paths = ["6.01__Simple_Interest_and_Discount.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Write a single multiple choice exercise on the topic of Interests. Generate the question as a json of scheme: {question: string, answer1: string, answer2:string, answer3: string, answer4: string, right_answer_explanation: string}",
)
# Use the create and poll SDK helper to create a run and poll the status of
# the run until it's in a terminal state.

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

message_content = messages[0].content[0].text
annotations = message_content.annotations
citations = []
for index, annotation in enumerate(annotations):
    message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
    if file_citation := getattr(annotation, "file_citation", None):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f"[{index}] {cited_file.filename}")

print(message_content.value)
print("\n".join(citations))
