import os
from openai import OpenAI

_client = OpenAI(
    api_key=os.environ["NVIDIA_API_KEY"],
    base_url="https://integrate.api.nvidia.com/v1",
)


def embed(text: str, input_type: str = "passage") -> list[float]:
    response = _client.embeddings.create(
        model="nvidia/nv-embedqa-e5-v5",
        input=text,
        extra_body={"input_type": input_type},
    )
    return response.data[0].embedding


if __name__ == "__main__":
    vec = embed("test transaction embedding")
    print(f"Vector length: {len(vec)}")
