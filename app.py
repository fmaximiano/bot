import os
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from openai import AzureOpenAI
import time
import requests

load_dotenv()

app = Flask(__name__)

client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key= os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-06-01 -preview",
)

assistant = os.getenv("ASSISTANT_ID")


def get_new_bot_response(prompt):

    # Create a thread
    thread = client.beta.threads.create()
    print(thread.id)

    # Add a user question to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

        
    
    # Run the thread
    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant
    )

    # Looping until the run completes or fails
    while run.status in ['queued', 'in_progress', 'cancelling']:
        print(run.status)
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id, order="asc"
        )
        messages_list = list(messages)
        response = messages_list[-1].content[0].text.value
        return response



def get_existing_bot_response(prompt):

    url = "https://fnc-seplagmg-faleconosco.azurewebsites.net/api/Chat?"

    body = {
        "key": os.getenv("FNC_KEY"),
        "pergunta": prompt
    }

    response = requests.post(url, json=body)
    return response.text


@app.route('/api/bot1', methods=['POST'])
def bot1():
    data = request.json
    prompt = data['prompt']
    response = get_new_bot_response(prompt)
    return jsonify({'response': response})

@app.route('/api/bot2', methods=['POST'])
def bot2():
    data = request.json
    prompt = data['prompt']
    response = get_existing_bot_response(prompt)
    return jsonify({'response': response}) 

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
