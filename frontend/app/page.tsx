"use client"; // Declare this file as a client component

import { useState } from "react"; // Import the useState hook from React for managing state

export default function Home() {
  const [message, setMessage] = useState(""); // Message entered by the user
  const [reply, setReply] = useState(""); // Reply from chatbot
  const [conversationId, setConversationId] = useState(null); // Conversation ID for the session
  const [history, setHistory] = useState(null);

  // Initialize a new conversation and get a conversation ID
  async function startConversation() {
    try {
      const response = await fetch("http://127.0.0.1:8000/start_conversation/", {
        method: "POST",
      });
      const data = await response.json();
      setConversationId(data.conversation_id); // Save the conversation ID
      setHistory([]);
      console.log("Conversation started. ID:", data.conversation_id);
    } catch (error) {
      setReply("Failed to start a conversation.");
      console.error("Error starting conversation:", error);
    }
  }

  // Send a message to the backend
  async function sendMessage() {
    if (!conversationId) {
      setReply("Please start a conversation first.");
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/chat/?conversation_id=${conversationId}`, // Include the conversation ID in the query
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json", // Indicate the request body as JSON
          },
          body: JSON.stringify({ content: message }), // Convert message state to JSON and include it in the request body
        }
      );

      if (!response.ok) {
        throw new Error("Failed to connect to the backend.");
      }

      const reader = response.body.getReader(); // Handle streaming response
      const decoder = new TextDecoder();
      let done = false;
      let fullReply = "";

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          fullReply += chunk;
        }
      }

      // update conversation history
      setHistory((prev) => [
        ...prev,
        { role: "user", content: message },
        { role: "assistant", content: fullReply },
      ]);
      setReply(fullReply); // Update the reply state with the chatbot's response
      setMessage(""); // clear the input field
    } catch (error) {
      setReply("Failed to connect to the chatbot.");
      console.error("Error sending message:", error);
    }
  }

  return (
    <main>
      <h1>Charchar's Web Chatbot</h1>
      {!conversationId ? (
        <button onClick={startConversation}>Start Conversation</button> // Button to initialize a conversation
      ) : (
        <div>
          <input
            type="text"
            placeholder="Type your message here..."
            value={message}
            onChange={(e) => setMessage(e.target.value)} // Update the message state when the user types
          />
          <button onClick={sendMessage}>Send</button> // Send the message
        </div>
      )}
      <p>Reply: {reply}</p> {/* Display the chatbot's reply */}
    </main>
  );
}