import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Привет!"}],
        max_tokens=50
    )
    print("SUCCESS:", response.choices[0].message.content)
except Exception as e:
    print("ERROR:", str(e))