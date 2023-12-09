import openai

def chat_with_openai(prompt, model="gpt-4", messages=[]):
    # Set up your API key from OpenAI
    openai.api_key = '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'

    # Construct the request payload
    request_payload = {
        "model": model,
        "messages": messages
    }

    # Add the new prompt to the conversation
    messages.append({"role": "user", "content": prompt})

    # Make a request to the chat model
    response = openai.ChatCompletion.create(**request_payload)

    return response.choices[0].message['content']

# Example usage:
response = chat_with_openai("https://datavisualization.nightowlspace.com/static/img/undraw_posting_photo.svg - describe the image")
print(response)
