from groq import Groq

print("Script started")
try:
    client = Groq(api_key="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")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": "Say 'API working' if you can read this"}
        ],
    )

    print("API call succeeded")
    print(response.choices[0].message.content)
except Exception as e:
    print("An error occurred:", e)