import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(model_key="FAST_MODEL"):
    return ChatOpenAI(
        base_url=os.getenv("NVIDIA_BASE_URL"),
        api_key=os.getenv("NVIDIA_API_KEY"),
        model=os.getenv(model_key)
    )

def test_model(name, model_key):
    print(f"\n{'─'*40}")
    print(f"Testing: {name}")
    print(f"Model:   {os.getenv(model_key)}")
    print(f"{'─'*40}")
    try:
        llm = get_llm(model_key)
        response = llm.invoke("In one sentence, what is fraud detection?")
        print(f"✅ Response: {response.content}")
    except Exception as e:
        print(f"❌ Failed: {e}")

def test_openrouter():
    name = "FALLBACK (OpenRouter)"
    model = os.getenv("OPENROUTER_MODEL")
    print(f"\n{'─'*40}")
    print(f"Testing: {name}")
    print(f"Model:   {model}")
    print(f"{'─'*40}")
    try:
        llm = ChatOpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model=model
        )
        response = llm.invoke("In one sentence, what is fraud detection?")
        print(f"✅ Response: {response.content}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_model("DETECTOR  (Llama 3.3 70B)",  "FAST_MODEL")
    test_model("INVESTIGATOR (Palmyra-Fin)", "FINANCE_MODEL")
    test_openrouter()
    
