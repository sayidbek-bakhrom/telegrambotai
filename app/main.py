from fastapi import FastAPI, HTTPException
import httpx
from .models import MessageRequest, SummarizeRequest
from app.logic import get_history, add_user_message, add_bot_response, get_client
from config import HF_TOKEN

app = FastAPI()


@app.post("/process_message")
async def process_message(req: MessageRequest):
    try:
        user_id = req.user_id

        # Retrieve the user's chat history
        user_history = get_history(user_id)
        add_user_message(user_id, req.message)

        # Prepare message history for the model
        messages = list(user_history)
        completion = get_client().chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct:novita",
            messages=messages,
        )

        ai_message = completion.choices[0].message.content

        # Save the bot response
        add_bot_response(user_id, ai_message)

        return {"response": ai_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": req.text}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from Hugging Face API")
        result = response.json()

    if isinstance(result, list) and "summary_text" in result[0]:
        return {"summary": result[0]["summary_text"]}
    else:
        return {"summary": "Sorry, could not generate a summary."}

@app.get("/")
async def root():
    return {"message": "API is running"}
