from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import re 
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

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
        async def stream_response():
            collected_content = []
            response = client.chat.completions.create(
                model="gpt-4",
                messages=manager.history,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    yield content
            
            # Store the complete response in history
            manager.add_message("assistant", "".join(collected_content))
            
        return StreamingResponse(stream_response(), media_type="text/plain")
    
    except Exception as e:
        if "timeout" in str(e).lower() or "service unavailable" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API is currently unavailable. Please try again later."
            )
        raise HTTPException(status_code=500, detail=str(e))
