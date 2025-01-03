from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from openai import OpenAI
import re 
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uuid
import sqlite3 

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # Drop existing tables if they exist 
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS conversations")   
    
    # recreate tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

class Message(BaseModel):
    content: str

class ConversationManager(): # manage conversation history
    def __init__(self):
        self.db_path = "chatbot.db"

    def create_conversation(self):
        conversation_id = str(uuid.uuid4()) # Generate a unique conversation ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (conversation_id) VALUES (?)",
            (conversation_id,)
        )
        conn.commit()
        conn.close()
        return conversation_id

    def add_message(self, conversation_id, role, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT conversation_id FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Conversation not found")
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        conn.commit()
        conn.close()

    def get_history(self, conversation_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conversation_id,)
        )
        history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return history

manager = ConversationManager()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API"}


@app.post("/start_conversation/")
def start_conversation():
    conversation_id = manager.create_conversation()
    return {"conversation_id": conversation_id}

@app.post("/chat/")
async def chat_with_gpt(
    message: Message,
    conversation_id: str = Query(..., description="Unique conversation ID")
):
    if not message.content.strip():  # check empty content
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    
    if not re.match(r"^[a-zA-Z0-9\s.,?!]*$", message.content): # This is quite restrictive
        raise HTTPException(status_code=400, detail="Message contains unsupported characters.")
    
    manager.add_message(conversation_id, 'user', message.content)

    try:
        async def stream_response():
            collected_content = []
            response = client.chat.completions.create(
                model="gpt-4",
                messages=manager.get_history(conversation_id),
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    yield content
            
            # Store the complete response in history
            manager.add_message(conversation_id, "assistant", "".join(collected_content))
            
        return StreamingResponse(stream_response(), media_type="text/plain")
    
    except Exception as e:
        if "timeout" in str(e).lower() or "service unavailable" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API is currently unavailable. Please try again later."
            )
        raise HTTPException(status_code=500, detail=str(e))