import React, { useState, useEffect, useRef } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import axios from 'axios';

const App = () => {
  const apiUrl = process.env.API_URL;
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [scenarioTasks, setScenarioTasks] = useState({"scenario": "", "tasks": [], "completed": []});

  const chatBoxRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    /**
     * Calling SCENARIO & TASKS end-point
     */
    const fetchScenarioTasks = async () => {
      try {
        const response = await axios.post(apiUrl + '/scenario-tasks/', {
          // we can put User's parameters like language, level, topic etc. here
        });

        setScenarioTasks(response.data);
        console.log("'scenarioTasks' var state:", scenarioTasks);
        console.log("Response from /scenario-tasks/:", response.data);
      } catch (error) {
        console.error("Error fetching scenario tasks:", error);
      }
    };

    fetchScenarioTasks();
  }, []);

  /**
   * Scroll to the bottom of the chat-box whenever messages are updated.
   */
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]); // Trigger whenever `messages` changes

  /**
   * Calling CHAT end-point
   */
  const handleSendMessage = async () => {
    const newMessage = { role: "user", text: inputMessage };
    const updatedMessages = [...messages, newMessage];
    const requestBody = {
      scenario: scenarioTasks.scenario,
      tasks: {
        task_list: scenarioTasks.tasks,
        completed: scenarioTasks.completed
      },
      messages: updatedMessages.filter(message => message.role !== "tutor"),
    }

    console.log(requestBody)

    const response = await axios.post(apiUrl + "/chat/", requestBody);
    console.log(response.data)

    if (response.data.lastMessageEvaluation) {
      updatedMessages.push({role: "tutor", text: response.data.lastMessageEvaluation})
    }

    if (response.data.subTaskCompletion) {
      setScenarioTasks((prevState) => ({
        ...prevState,
        completed: [...prevState.completed, response.data.subTaskCompletion],
      }));
    }

    if (response.data.role == "assistant") {
      updatedMessages.push({role: "assistant", text: response.data.text})
    }

    setMessages(updatedMessages);
    setInputMessage("");  // Reset input field

    // Focus on the input field
    inputRef.current && inputRef.current.focus();
  };

  return (
    <div className="container mt-5">
      <div className="row">
        <div className="col-md-3">
          {/* Scenario Panel */}
          <div className="card">
            <div className="card-body">
              <h4>Scenario</h4>
              <p>{scenarioTasks.scenario ? scenarioTasks.scenario : ""}</p>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          {/* Chat Panel */}
          <div className="card chat-panel">
            <div className="card-body">
              <h4>Chat with the AI</h4>
              <div className="chat-box" ref={chatBoxRef}>
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`alert ${
                      msg.role === "user" ? 'alert-primary' :
                      msg.role === "assistant" ? 'alert-secondary' : 'alert-info' // For 'tutor'
                    } message-content`}
                  >
                    <strong>{msg.role === "user" ? "You:" : msg.role === "assistant" ? "AI:" : "Tutor:\n"} </strong>
                    {msg.text}
                  </div>
                ))}
              </div>
              <div className="mt-3">
                <form onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}>
                  <input
                    type="text"
                    ref={inputRef}
                    className="form-control"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type your message..."
                  />
                  <button type='submit' className="btn btn-primary mt-2">Send</button>
                </form>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          {/* Task Panel */}
          <div className="card">
            <div className="card-body">
              <h4>Your Tasks</h4>
              <ul>
                {scenarioTasks.tasks.map((task, index) => (
                <li key={index}>
                  <input
                    id={`task-${index + 1}`}
                    type="checkbox"
                    checked={scenarioTasks.completed.includes(index + 1)}
                    disabled
                    className={scenarioTasks.completed.includes(index + 1) ? "checkbox-checked" : "checkbox-unchecked"}
                  />
                  {' '}
                  {task}
                </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
