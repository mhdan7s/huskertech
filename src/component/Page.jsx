import React, { useEffect, useRef, useState } from "react";
import image from "../assets/images.jpeg";
import user from "../assets/user.png";
import ReactMarkdown from "react-markdown";

export const Page = () => {
  const [userValue, setUserValue] = useState("");
  const [message, setMessage] = useState([]);
  const [initialState, setInitialState] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const messageRef = useRef(null);

  const handleInputMessage = () => {
    if (userValue.trim() === "") {
      return;
    }

    const newMessage = {
      id: Date.now(),
      text: userValue,
      sender: "user",
    };

    setMessage((prevMessages) => [...prevMessages, newMessage]);
    const currentQuestion = userValue;
    setUserValue("");

    if (initialState) {
      setInitialState(false);
    }

    setIsTyping(true);

    fetch("http://127.0.0.1:5000/api/rag", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: currentQuestion }),
    })
      .then((response) => response.json())
      .then((data) => {
        const reply = {
          id: Date.now() + 1,
          text: data.answer,
          sender: "ai",
        };
        setMessage((prevMessages) => [...prevMessages, reply]);
      })
      .catch((error) => {
        console.error("Error fetching AI response:", error);
        const errorReply = {
          id: Date.now() + 1,
          text: "Sorry, something went wrong. Please try again.",
          sender: "ai",
        };
        setMessage((prevMessages) => [...prevMessages, errorReply]);
      })
      .finally(() => {
        setIsTyping(false);
      });
  };

  useEffect(() => {
    if (messageRef.current) {
      messageRef.current.scrollTop = messageRef.current.scrollHeight;
    }
  }, [message]);

  const duo = () => {
    const userValue =
      "I am getting bypass code on my screen when I try to login?";
    if (userValue.trim() === "") {
      return;
    }

    const newMessage = {
      id: Date.now(),
      text: userValue,
      sender: "user",
    };

    setMessage((prevMessages) => [...prevMessages, newMessage]);
    const currentQuestion = userValue;
    setUserValue("");

    if (initialState) {
      setInitialState(false);
    }

    setIsTyping(true);
    fetch("http://127.0.0.1:5000/api/duo", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: currentQuestion }),
    })
      .then((response) => response.json())
      .then((data) => {
        const reply = {
          id: Date.now() + 1,
          text: data.answer,
          sender: "ai",
        };
        setMessage((prevMessages) => [...prevMessages, reply]);
      })
      .catch((error) => {
        console.error("Error fetching AI response:", error);
        const errorReply = {
          id: Date.now() + 1,
          text: "Sorry, something went wrong. Please try again.",
          sender: "ai",
        };
        setMessage((prevMessages) => [...prevMessages, errorReply]);
      })
      .finally(() => {
        setIsTyping(false);
      });
  };


  return (
    <div>
      {initialState && <div className="body">What Can We Help With?</div>}

      {!initialState && (
        <>
          <div className="main-body" ref={messageRef}>
            {message.map((msg) => (
              <div
                key={msg.id}
                className={`message ${
                  msg.sender === "user" ? "user-message" : "ai-message"
                } ai-response-text markdown-content`}
              >
                {msg.sender === "user" ? (
                  <img src={user} alt="AI Icon" className="chat-icon" />
                ) : (
                  <img src={image} alt="User Icon" className="chat-icon" />
                )}
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            ))}
            {isTyping && (
              <div className="message ai-message">
                <p style={{ margin: 0 }}>Typing...</p>
              </div>
            )}
          </div>
        </>
      )}

      <div className="main-page">
        <input
          className="footer-input"
          placeholder="Ask Us"
          value={userValue}
          onChange={(e) => setUserValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleInputMessage();
            }
          }}
          style={{
            marginTop: initialState === false ? "10px" : "0px",
          }}
        />
      </div>

      {initialState && (
        <div className="page">
          <div className="page-options">
            <button
              className="page-options"
              onClick={() => handleClick("HARDWARE")}
            >
              HARDWARE
            </button>
            <button
              className="page-options"
              onClick={() => handleClick("SOFTWARE")}
            >
              SOFTWARE
            </button>
            <button className="page-options" onClick={() => duo()}>
              DUO
            </button>
            <button
              className="page-options"
              onClick={() => handleClick("NETWORK")}
            >
              NETWORK
            </button>
          </div>
          <div className="page-options">
            <button
              className="page-options"
              onClick={() => {
                // apiCall();
              }}
            >
              TICKETS
            </button>
            <button
              className="page-options"
              onClick={() => handleClick("PASSWORD")}
            >
              PASSWORD
            </button>
            <button
              className="page-options"
              onClick={() => handleClick("CLASSROOM")}
            >
              CLASSROOM
            </button>
            <button
              className="page-options"
              onClick={() => handleClick("MORE")}
            >
              MORE
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
