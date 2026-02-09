from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
logger.debug("Client created")


class Request(BaseModel):
    language: str
    framework: str
    source: str


@app.get("/")
async def root():
    logger.debug("Received ping")
    return {"message": "Ok"}


@app.put("/get-tests/")
async def get_tests(request: Request):
    logger.debug("Received request")
    return generate_tests(request.language, request.framework, request.source)


def generate_tests(language, framework, source_code):
    global client
    prompt = f"""
You are an expert software engineer and test automation specialist.
Your task is to generate **comprehensive, clean, and idiomatic unit tests** for the provided source code.

Requirements:
- Language: {language}
- Test framework: {framework}
- Follow best practices for this language and framework.
- Cover edge cases and invalid inputs.
- Include clear test method names.
- Do not rewrite the source code, only provide test code.
- Do not add explanations or comments unless specifically requested.
- Return only valid, compilable test code.

Source code:
\"\"\"
{source_code}
\"\"\"
"""
    resp = client.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content.strip()

