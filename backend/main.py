from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import re 
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API"}

class Message(BaseModel):
    content: str

# MAX_HISTORY_LENGTH = 20 # limit conversation length to prevent too much storage

class ConversationManager(): # manage conversation history
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append({'role': role, 'content': content})

manager = ConversationManager()

@app.post("/chat/")
async def chat_with_gpt(message: Message):
    if not message.content.strip():  # check empty content
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    
    if not re.match(r"^[a-zA-Z0-9\s.,?!]*$", message.content): # check illegal symbols
        raise HTTPException(status_code=400, detail="Message contains unsupported characters.")
    
    manager.add_message('user', message.content)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=manager.history
        )
        reply = response.choices[0].message.content

        # add user messaged to conversation history
        manager.add_message("assistant", reply)
        
        return {"reply": reply}
    
    except (openai.error.Timeout, openai.error.ServiceUnavailableError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API is currently unavailable. Please try again later."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

