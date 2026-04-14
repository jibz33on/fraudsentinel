import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools.logger import get_logger

load_dotenv()

logger = get_logger("LLM_ROUTER")

MAX_RETRIES = 3
RETRY_DELAY = 1
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# def _get_nvidia_llm(model_key: str) -> ChatOpenAI:
#     return ChatOpenAI(
#         base_url=os.getenv("NVIDIA_BASE_URL"),
#         api_key=os.getenv("NVIDIA_API_KEY"),
#         model=os.getenv(model_key),
#     )


def _get_groq_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
        model=GROQ_MODEL,
    )


def _get_openrouter_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model=os.getenv("OPENROUTER_MODEL"),
    )


def call_llm(prompt: str, model_key: str = "FAST_MODEL") -> str:
    # Try Groq with retries
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Groq attempt {attempt}/{MAX_RETRIES} (model: {GROQ_MODEL})")
            llm = _get_groq_llm()
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.warning(f"Groq attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    # Fallback to OpenRouter
    try:
        logger.info(f"Switching to OpenRouter fallback (model: {os.getenv('OPENROUTER_MODEL')})")
        llm = _get_openrouter_llm()
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"OpenRouter fallback also failed: {e}")
        raise RuntimeError(f"All LLM providers failed. Last error: {e}")


# To switch back to NVIDIA, uncomment _get_nvidia_llm() above
# and replace _get_groq_llm() calls with _get_nvidia_llm(model_key)


if __name__ == "__main__":
    result = call_llm("In one sentence, what is fraud detection?")
    print(f"\nResult: {result}")