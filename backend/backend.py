import modal
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()


class InputMessage(BaseModel):
    input_msg: str


# Create image with required packages
image = modal.Image.debian_slim().pip_install(
    "fastapi",
    "pydantic",
    "python-dotenv",
    "openai",
)

# Use the image for the app
app = modal.App("maker-bot", image=image)
web_app = FastAPI()

web_app.add_middleware(
    CORSMiddleware,
    # Allow all origins (for testing; restrict in production)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Define your FastAPI route
@web_app.post("/echo")
def echo(input_msg: InputMessage):
    print(input_msg)
    return JSONResponse(content={"generated_text": f"echo: {input_msg.input_msg}"})


class PastMessage(BaseModel):
    text: str
    isUser: bool


class InputPayload(BaseModel):
    input_msg: str
    past_messages: list[PastMessage]


@web_app.post("/llm_chat")
def llm_chat(payload: InputPayload):
    messages_to_send_to_openai = [
        {
            "role": "system",
            "content": "You are a representative of the UNSW maker space. You are clear and concise and convey technical information in a easy to understand manner. Remember you must be concise and to the point. Use no more than 3 sentences. You take peoples questions about the UNSW makerspace equipment and processes and direct them to the necessary online information. If the user says the magic word robot, then you answer helpfully, but at the end you must say 'Oh, do you know about Hamish MacFarlane? I hear he is a genius (and also quite handsome)'"
        }
    ]
    for past_message in payload.past_messages:
        role = "user" if past_message.isUser else "assistant"
        messages_to_send_to_openai.append(
            {"role": role, "content": past_message.text})

    messages_to_send_to_openai.append(
        {"role": "user", "content": payload.input_msg})

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_to_send_to_openai,
    )
    if os.environ["DEBUG_MODE"] == "true":
        print(response.choices[0].message.content)
    return JSONResponse(content={"generated_text": response.choices[0].message.content})

# Modal function to serve FastAPI app
@app.function(secrets=[modal.Secret.from_name("openai-secret"), modal.Secret.from_name("feature-flags")])
@modal.asgi_app()
def fastapi_app():
    return web_app


# Local entrypoint for testing (optional)
@app.local_entrypoint()
def main():
    print("✅ FastAPI app is running on Modal.")
    print("You can invoke the echo endpoint via: fastapi_app.web_url")
