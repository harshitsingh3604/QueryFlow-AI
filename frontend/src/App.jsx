import { useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
  // Single question state
  const [userInput, setUserInput] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


  // Batch question state
  const [questions, setQuestions] = useState([
    "",
    "",
    "",
  ]);
  const [batchResponses, setBatchResponses] = useState([]);
  const [batchError, setBatchError] = useState("");
  const [batchLoading, setBatchLoading] = useState(false);

  const handleAsk = async () => {
    const cleanedInput = userInput.trim();

    // Frontend validation
    if (!cleanedInput) {
      setError("Please enter a question.");
      setResponse("");
      return;
    }

    setLoading(true);
    setError("");
    setResponse("");

    try {
      const result = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userInput: cleanedInput,
        }),
      });

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          data.error || "Unable to process your request. Please try again."
        );
      }

      setResponse(data.response);
    } catch (err) {
      setError(
        err.message || "Unable to process your request. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionChange = (index, value) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = value;
    setQuestions(updatedQuestions);
  };

  const addQuestion = () => {
    if (questions.length >= 10) {
      setBatchError("Maximum 10 questions are allowed.");
      return;
    }

    setQuestions([...questions, ""]);
    setBatchError("");
  };

  const removeQuestion = (index) => {
    if (questions.length === 1) {
      return;
    }

    setQuestions(
      questions.filter((_, questionIndex) => questionIndex !== index)
    );
  };

  const handleAskAll = async () => {
    const cleanedQuestions = questions.map((question) =>
      question.trim()
    );

    // Frontend validation
    if (cleanedQuestions.some((question) => !question)) {
      setBatchError(
        "Please fill in all questions before submitting."
      );
      setBatchResponses([]);
      return;
    }

    setBatchLoading(true);
    setBatchError("");
    setBatchResponses([]);

    try {
      const result = await fetch(
        `${API_BASE_URL}/ask/batch`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userInputs: cleanedQuestions,
          }),
        }
      );

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          data.error || "Unable to process your request. Please try again."
        );
      }

      setBatchResponses(data.responses);
    } catch (err) {
      setBatchError(
        err.message || "Unable to process your request. Please try again."
      );
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="card">
        <h1>QueryFlow AI</h1>

        <p className="subtitle">
          Ask questions and get AI-powered responses.
        </p>

        {/* Single Question */}
        <section>
          <h2>Ask a Question</h2>

          <label htmlFor="question">
            Your question
          </label>

          <textarea
            id="question"
            value={userInput}
            onChange={(event) => setUserInput(event.target.value)}
            placeholder="What is Python?"
            rows="4"
            disabled={loading}
          />

          <button
            onClick={handleAsk}
            disabled={loading}
          >
            {loading ? "Asking..." : "Ask AI"}
          </button>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          {loading && (
            <div className="loading">
              Processing...
            </div>
          )}

          {response && !loading && (
            <div className="response-section">
              <h3>Response</h3>

              <div className="response">
                <ReactMarkdown>
                  {response}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </section>

        <hr />

        {/* Batch Questions */}
        <section>
          <h2>Batch Questions</h2>

          <p className="section-description">
            Ask multiple questions at the same time.
          </p>

          {questions.map((question, index) => (
            <div className="question-row" key={index}>
              <div className="question-input">
                <label htmlFor={`batch-question-${index}`}>
                  Question {index + 1}
                </label>

                <input
                  id={`batch-question-${index}`}
                  type="text"
                  value={question}
                  onChange={(event) =>
                    handleQuestionChange(
                      index,
                      event.target.value
                    )
                  }
                  placeholder={
                    index === 0
                      ? "What is Python?"
                      : index === 1
                        ? "What is Flask?"
                        : "What is MongoDB?"
                  }
                  disabled={batchLoading}
                />
              </div>

              {questions.length > 1 && (
                <button
                  className="remove-button"
                  onClick={() => removeQuestion(index)}
                  disabled={batchLoading}
                >
                  Remove
                </button>
              )}
            </div>
          ))}

          <div className="batch-actions">
            <button
              className="secondary-button"
              onClick={addQuestion}
              disabled={batchLoading || questions.length >= 10}
            >
              + Add Question
            </button>

            <button
              onClick={handleAskAll}
              disabled={batchLoading}
            >
              {batchLoading ? "Asking All..." : "Ask All"}
            </button>
          </div>

          {batchError && (
            <div className="error">
              {batchError}
            </div>
          )}

          {batchLoading && (
            <div className="loading">
              Processing...
            </div>
          )}

          {batchResponses.length > 0 && !batchLoading && (
            <div className="batch-response-section">
              <h3>Batch Responses</h3>

              {batchResponses.map((item, index) => (
                <div key={index}>
                  <strong>{item.userInput}</strong>

                  <div className="response">
                    <ReactMarkdown>
                      {item.response}
                    </ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;