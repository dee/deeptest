from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from loguru import logger
from openai import OpenAI, APITimeoutError
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()
api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("DeepSeek API key not found!")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
logger.debug("Client created")


class GenerateTestsRequest(BaseModel):
    language: str = Field(min_length = 1, max_length = 50)
    framework: str = Field(min_length = 1, max_length = 50)
    source: str = Field(min_length = 1, max_length = 50000)


class GenerateTestsResponse(BaseModel):
    tests: str


@app.get("/")
def root():
    logger.debug("Received ping")
    return {"message": "Ok"}


@app.post("/get-tests/")
def get_tests(request: GenerateTestsRequest):
    logger.debug("Received request")
    return GenerateTestsResponse(tests = generate_tests(request.language, request.framework, 
        request.source))


def generate_tests(language, framework, source_code):
    global client
    prompt = f"""
You are an expert software engineer and test automation specialist.
Your task is to generate **comprehensive, clean, and idiomatic unit tests** for the 
provided source code.

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
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except APITimeoutError:
        logger.error("A request timeout was reached.")
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, 
            detail="Request to DeepSeek timed out")
