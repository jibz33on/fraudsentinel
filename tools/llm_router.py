import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAI as OpenAIClient
from tools.logger import get_logger

load_dotenv()

logger = get_logger("LLM_ROUTER")

MAX_RETRIES  = 3
RETRY_DELAY  = 1
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"
OPENAI_MODEL = "gpt-4o-mini"


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


def _call_openai(prompt: str) -> str | None:
    """Call OpenAI gpt-4o-mini directly. Returns None on 429 or missing key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        client = OpenAIClient(api_key=api_key)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "429" in err or "rate_limit" in err.lower():
            logger.warning(f"OpenAI 429 rate limit — skipping to next provider")
        else:
            logger.warning(f"OpenAI failed: {e}")
        return None


def call_llm(prompt: str, model_key: str = "FAST_MODEL") -> str | None:
    # 1. Try Groq with retries
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Groq attempt {attempt}/{MAX_RETRIES} (model: {GROQ_MODEL})")
            llm = _get_groq_llm()
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower():
                logger.warning(f"Groq 429 rate limit on attempt {attempt} — moving to next provider")
                break
            logger.warning(f"Groq attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    # 2. Try OpenAI
    logger.info(f"Switching to OpenAI (model: {OPENAI_MODEL})")
    result = _call_openai(prompt)
    if result is not None:
        return result

    # 3. Fallback to OpenRouter
    try:
        logger.info(f"Switching to OpenRouter fallback (model: {os.getenv('OPENROUTER_MODEL')})")
        llm = _get_openrouter_llm()
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"All LLM providers failed. Last error: {e}")
        return None


# To switch back to NVIDIA, uncomment _get_nvidia_llm() above
# and replace _get_groq_llm() calls with _get_nvidia_llm(model_key)


if __name__ == "__main__":
    result = call_llm("In one sentence, what is fraud detection?")
    print(f"\nResult: {result}")