import ollama

response = ollama.chat(
    model="llama3",
    messages=[
        {"role": "system", "content": "You are Jarvis, an intelligent virtual assistant."},
        {"role": "user", "content": "What is programming?"}
    ]
)

print(response["message"]["content"])
