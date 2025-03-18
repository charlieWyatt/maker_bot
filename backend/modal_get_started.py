import modal
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI


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
app = modal.App("example-fastapi-echo", image=image)
web_app = FastAPI()

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing; restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)



# Define your FastAPI route
@web_app.post("/echo")
def echo(input_msg: InputMessage):
    print(input_msg)
    return JSONResponse(content={"generated_text": f"echo: {input_msg.input_msg}"})

@web_app.post("/llm_chat")
def llm_chat(input_msg: InputMessage):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You Love Modal labs. You enthusiastically try and get to know the user, and then ask them any questions about modal labs. You also love relevanceAI too."},
            {"role": "user", "content": input_msg.input_msg}
        ]
    )
    return JSONResponse(content={"generated_text": response.choices[0].message.content})

# Modal function to serve FastAPI app
@app.function(secrets=[modal.Secret.from_name("openai-secret")])
@modal.asgi_app()
def fastapi_app():
    return web_app


# Local entrypoint for testing (optional)
@app.local_entrypoint()
def main():
    print("✅ FastAPI app is running on Modal.")
    print("You can invoke the echo endpoint via: fastapi_app.web_url")