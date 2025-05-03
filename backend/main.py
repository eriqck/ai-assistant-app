from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# For now, we'll use this simple in-memory store for history
chat_history = []

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(data: Question, background_tasks: BackgroundTasks):
    question = data.question

    # Call AI function
    answer = get_ai_response(question)

    # Log the question and answer in the background
    background_tasks.add_task(log_interaction, question, answer)

    return {"question": question, "answer": answer}

def get_ai_response(question: str) -> str:
    #call OpenAI API
    try:
        response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You're a helpful AI answering FAQs."},
                {"role": "user", "content": question}
        ],

        temperature=0.7
    )

        answer = response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

    
def log_interaction(q, a):
    chat_history.append({"question": q, "answer": a})
    print(f"Logged: {q} => {a}")

@app.get("/history")
def get_history():
    return chat_history
