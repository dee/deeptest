from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from loguru import logger
from openai import OpenAI, APITimeoutError, APIConnectionError
from dotenv import load_dotenv
import os
import time

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


@app.post("/tests")
def get_tests(request: GenerateTestsRequest):
    logger.debug("Received request")
    # i use monotonic just in case system clock changes during the request
    request_start = time.monotonic()
    response = GenerateTestsResponse(tests = generate_tests(request.language, request.framework, 
        request.source))
    duration = time.monotonic() - request_start
    logger.debug(f"Request took {duration:.2f} s")
    return response


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
    except APIConnectionError:
        logger.error("Failed to connect to API")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Request to DeepSeek timed out")
    except Exception as e:
        logger.exception("Unexpected error during DeepSeek call")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error")
