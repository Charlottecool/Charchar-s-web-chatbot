"use client"; // declare this file as a client component, make it run in the browser

import { useState } from "react"; // import the useState hook from React for managing state

export default function Home() {
  const [message, setMessage] = useState(""); // message entered by user
  const [reply, setReply] = useState("");// reply from chatbot

  async function sendMessage() { //send a message to backend
    try {
      // send post request to the backend api
      const response = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // indicate the request body as JSON
        },
        body: JSON.stringify({ content: message }), // convert message state to JSON and include it in the request body
      });

      if (!response.ok) {
        throw new Error("Failed to connect to the backend.");
      }

      const data = await response.json(); // Parse the JSON response from the backend
      setReply(data.reply); // Update the reply state with the chatbot's response
    } catch (error) {
      setReply("Failed to connect to the chatbot.");
    }
  }

  return (
    <main>
      <h1>Charchar's Web Chatbot</h1>
      <input
        type="text" // input type as text
        placeholder="Type your message here..."
        value={message}
        onChange={(e) => setMessage(e.target.value)} // Update the message state when the user types
      />
      <button onClick={sendMessage}>Send</button>
      <p>Reply: {reply}</p>
    </main>
  );
}

// # todo:
// style the page more
// add more interaction using keyboard instead of mouse