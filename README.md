# Charchar's Web Chatbot

A simple web-based chatbot application that allows users to interact with an AI chatbot. The frontend is built with React using Next.js, while the backend is powered by FastAPI. The chatbot connects to OpenAI's API for generating responses.

---

## Features

- Users can type messages in a text input field.
- Messages are sent to the backend, which processes the request and returns a reply from OpenAI's API.
- Replies are displayed in real-time on the web interface.

---

## Project Structure

```
project/
│
├── backend/                     # Backend code
│   ├── main.py                  # FastAPI backend implementation
│   ├── requirements.txt         # Backend dependencies
│
├── frontend/                    # Frontend code
│   ├── app/page.tsx             # React-based chatbot interface
│   ├── package.json             # Frontend dependencies
│
└── README.md                    # Project documentation
```

---

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- **Node.js** (16 or higher)
- **Python** (3.9 or higher)
- **Git**

---

## Installation

### **1. Clone the repository**
```bash
git clone git@github.com:Charlottecool/Charchar-s-web-chatbot.git
cd Charchar-s-web-chatbot
```

### **2. Setup the backend**

Navigate to the `backend/` folder:
```bash
cd backend
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the backend server:
```bash
uvicorn main:app --reload
```

By default, the backend will run at `http://127.0.0.1:8000`.

---

### **3. Setup the frontend**

Navigate to the `frontend/` folder:
```bash
cd ../frontend
```

Install dependencies:
```bash
npm install
```

Start the frontend development server:
```bash
npm run dev
```

By default, the frontend will run at `http://localhost:3000`.

---

## Usage

1. Open your browser and navigate to `http://localhost:3000`.
2. Type a message into the input field and press "Send".
3. The chatbot's response will appear below the input field.

---

## File Details

### **Backend (`main.py`)**
- Handles POST requests at `/chat/`.
- Sends the user's message to OpenAI's API and returns the chatbot's reply.

### **Frontend (`page.tsx`)**
- Contains the React component for the user interface.
- Manages state using `useState` for user messages and chatbot replies.
- Sends API requests to the backend using `fetch`.

---

## Example Interaction

- **User Input**: "Hello, chatbot!"
- **Chatbot Reply**: "Hi there! How can I assist you today?"

---

## Troubleshooting

1. **Cross-Origin Resource Sharing (CORS) Errors**:
   - Ensure the backend allows requests from `http://localhost:3000`.
   - Check that `CORSMiddleware` is configured in `main.py`.

2. **Backend Not Running**:
   - Make sure you have started the FastAPI server using `uvicorn`.

3. **Frontend Errors**:
   - Check for any errors in the browser console.
   - Verify the backend URL in `fetch` is correct (`http://127.0.0.1:8000/chat/`).

---

## Dependencies

### **Backend**
- FastAPI
- Uvicorn
- OpenAI

### **Frontend**
- React
- Next.js

---

## Author

- **Charlottecool** - [Your GitHub Profile](https://github.com/Charlottecool)

Feel free to open issues or submit pull requests for improvements!
```
