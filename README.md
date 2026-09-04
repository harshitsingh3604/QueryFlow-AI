# QueryFlow AI

QueryFlow AI is a full-stack AI question-answering application built using React, Flask, MongoDB, and a mock AI service.

The application supports both single-question and batch-question processing. Batch requests are processed concurrently while preserving the original order of responses.

---

## 1. Project Overview

QueryFlow AI allows users to submit questions through a React frontend.

The Flask backend receives the questions, retrieves a prompt template from MongoDB, replaces the `{{userInput}}` placeholder with the user's question, sends the generated prompt to the AI service, and stores request/response history in MongoDB.

### Main capabilities

- Single-question processing
- Batch-question processing
- Concurrent AI processing
- Ordered batch responses
- MongoDB-based prompt management
- Request/response history
- Input validation
- Error handling
- React frontend

---

## 2. Problem Statement

The objective is to build an API-driven AI question-answering system where prompts are dynamically retrieved from MongoDB instead of being hard-coded inside API routes.

For every request, the system should:

1. Accept the user's question.
2. Retrieve the required prompt template from MongoDB.
3. Replace `{{userInput}}` with the user's question.
4. Send the final prompt to the AI service.
5. Return the AI response.
6. Store the request and response in MongoDB.
7. Support multiple questions through a batch API.
8. Process batch AI calls concurrently.
9. Preserve the original order of batch responses.

---

## 3. Features

### Single Question

- Accepts one question using `POST /ask`
- Validates user input
- Retrieves prompt template from MongoDB
- Replaces `{{userInput}}`
- Generates an AI response
- Saves request/response history
- Returns a JSON response

### Batch Questions

- Accepts multiple questions using `POST /ask/batch`
- Supports up to 10 questions per request
- Validates every question
- Generates prompts dynamically
- Processes AI calls concurrently
- Preserves original input order
- Handles individual AI failures
- Stores batch results in MongoDB history

### Frontend

- React + Vite
- Single-question interface
- Dynamic batch question fields
- Add/remove questions
- Loading states
- Error handling
- Batch response display
- Responsive dark-themed UI

---

## 4. Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- Flask
- Flask-CORS

### Database

- MongoDB
- MongoDB Atlas
- PyMongo

### Testing

- pytest
- unittest.mock

### AI

The current implementation uses a local mock AI service for development and testing.

The AI service is separated from the API routes so a real AI provider can be integrated later.

---

## 5. Architecture

```text
                         React Frontend
                              |
                              | HTTP
                              v
                       Flask REST API
                       /                               /ask              /ask/batch
                    |                    |
                    v                    v
              MongoDB Prompt      MongoDB Prompt
                    |                    |
                    v                    v
                AI Service       Concurrent AI Calls
                                         |
                                         v
                                  Ordered Responses
                                         |
                                         v
                                  MongoDB History
                                         |
                                         v
                                   React Frontend
```

### Single Request Flow

```text
React
  ↓
POST /ask
  ↓
Flask
  ↓
Retrieve prompt from MongoDB
  ↓
Replace {{userInput}}
  ↓
AI Service
  ↓
Save history to MongoDB
  ↓
Return response
  ↓
React
```

### Batch Request Flow

```text
React
  ↓
POST /ask/batch
  ↓
Flask
  ↓
Retrieve prompt from MongoDB
  ↓
Build prompts for all questions
  ↓
Concurrent AI calls
  ↓
Preserve original order
  ↓
Save results to MongoDB history
  ↓
Return ordered responses
  ↓
React
```

---

## 6. Project Structure

```text
QueryFlow-AI/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   └── ai_routes.py
│   │   ├── services/
│   │   │   ├── prompt_service.py
│   │   │   ├── ai_service.py
│   │   │   └── history_service.py
│   │   └── database/
│   │       └── mongodb.py
│   ├── scripts/
│   │   └── seed_database.py
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_ask.py
│   │   └── test_batch.py
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   ├── run.py
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── ...
│
└── README.md
```

---

## 7. Prerequisites

Install the following:

- Python 3.10+
- Node.js
- npm
- MongoDB Atlas account or local MongoDB
- Git

---

## 8. Environment Variables

Create a `.env` file inside the `backend` directory.

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=intucate_case_study
AI_API_KEY=your_ai_api_key
```

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB connection string |
| `DATABASE_NAME` | MongoDB database name |
| `AI_API_KEY` | API key for a real AI provider if used |

The `.env` file contains sensitive information and should not be committed to Git.

A `.env.example` file is provided as a template.

---

## 9. MongoDB Setup

Create a MongoDB database named:

```text
intucate_case_study
```

Create these collections:

```text
prompts
history
```

### prompts Collection

Insert:

```json
{
  "_id": "Education_Prompt",
  "template": "You are an expert in education domain. Answer the following: {{userInput}}"
}
```

The backend retrieves this template dynamically from MongoDB.

### history Collection

Each successful request is stored in `history`.

Example:

```json
{
  "promptId": "Education_Prompt",
  "userInput": "What is Python?",
  "prompt": "You are an expert in education domain. Answer the following: What is Python?",
  "response": "[Mock AI Response] ...",
  "createdAt": "..."
}
```

---

## 10. Running Backend

Navigate to the backend:

```powershell
cd "C:\Users\Harshit\Desktop\QueryFlow AI\backend"
```

Activate the virtual environment:

```powershell
.\venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start Flask:

```powershell
python run.py
```

Backend URL:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/health
```

Expected:

```json
{
  "status": "ok"
}
```

---

## 11. Running Frontend

Open another terminal:

```powershell
cd "C:\Users\Harshit\Desktop\QueryFlow AI\frontend"
```

Install dependencies:

```powershell
npm install
```

Start Vite:

```powershell
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

Make sure the Flask backend is running before submitting questions.

---

## 12. API Documentation

### POST /ask

Processes a single question.

#### Endpoint

```text
POST http://127.0.0.1:5000/ask
```

#### Request

```json
{
  "userInput": "What is Python?"
}
```

#### Response

```json
{
  "response": "[Mock AI Response] ..."
}
```

#### Success Status

```text
200 OK
```

#### Invalid Request

```json
{
  "userInput": ""
}
```

Response:

```json
{
  "error": "userInput is required and must be a non-empty string"
}
```

Status:

```text
400 Bad Request
```

---

### POST /ask/batch

Processes multiple questions in a single request.

#### Endpoint

```text
POST http://127.0.0.1:5000/ask/batch
```

#### Request

```json
{
  "userInputs": [
    "What is Python?",
    "What is Flask?",
    "What is MongoDB?"
  ]
}
```

#### Response

```json
{
  "responses": [
    {
      "userInput": "What is Python?",
      "response": "[Mock AI Response] ..."
    },
    {
      "userInput": "What is Flask?",
      "response": "[Mock AI Response] ..."
    },
    {
      "userInput": "What is MongoDB?",
      "response": "[Mock AI Response] ..."
    }
  ]
}
```

#### Success Status

```text
200 OK
```

#### Batch Limit

The maximum batch size is 10 questions.

A request containing more than 10 questions returns:

```json
{
  "error": "Maximum batch size is 10"
}
```

with status:

```text
400 Bad Request
```

---

## 13. Async Processing

Batch AI calls are processed concurrently using Python's `ThreadPoolExecutor`.

AI/API calls are primarily I/O-bound, so concurrent execution reduces unnecessary waiting.

Without concurrency:

```text
Question 1 → AI → Wait
Question 2 → AI → Wait
Question 3 → AI → Wait
```

With concurrency:

```text
Question 1 ─┐
Question 2 ─┼──→ Concurrent AI calls
Question 3 ─┘
```

The batch size is limited to 10 to control resource usage.

---

## 14. Response Ordering

Concurrent tasks may finish in a different order from their submission order.

For example:

```text
Input:
A
B
C
```

The calls might finish as:

```text
B
C
A
```

The application collects futures in the original input order, so the API returns:

```text
A
B
C
```

This provides deterministic results to the frontend.

---

## 15. Error Handling

### Single API

Handled cases include:

- Missing JSON body
- Missing `userInput`
- Empty `userInput`
- Whitespace-only input
- Invalid input type
- Prompt not found
- MongoDB errors
- AI service errors
- Internal server errors

### Batch API

Handled cases include:

- Missing JSON body
- Missing `userInputs`
- Empty array
- More than 10 questions
- Invalid item type
- Empty question
- MongoDB errors
- AI service failures

For batch requests, an individual AI failure can be represented as an error for that item instead of failing the complete batch.

Example:

```json
{
  "responses": [
    {
      "userInput": "Question A",
      "response": "..."
    },
    {
      "userInput": "Question B",
      "error": "AI service unavailable"
    }
  ]
}
```

---

## 16. Database Schema

### prompts

```json
{
  "_id": "Education_Prompt",
  "template": "You are an expert in education domain. Answer the following: {{userInput}}"
}
```

### history

A successful request creates a document similar to:

```json
{
  "promptId": "Education_Prompt",
  "userInput": "What is Python?",
  "prompt": "You are an expert in education domain. Answer the following: What is Python?",
  "response": "[Mock AI Response] ...",
  "createdAt": "..."
}
```

For batch requests, each question creates its own history entry.

---

## 17. Testing

The backend uses `pytest`.

Run all tests from the backend directory:

```powershell
python -m pytest -q
```

Tests cover:

- Health endpoint
- Single-question API
- Valid input
- Missing input
- Empty input
- Invalid input
- AI failure handling
- Batch API
- Empty batch
- Invalid batch input
- Batch response count
- Response ordering
- Concurrent processing

The application can also be manually tested end-to-end through the React frontend.

### Single End-to-End Flow

```text
React
 ↓
POST /ask
 ↓
Flask
 ↓
MongoDB
 ↓
AI Service
 ↓
MongoDB History
 ↓
React
```

### Batch End-to-End Flow

```text
React
 ↓
POST /ask/batch
 ↓
Flask
 ↓
MongoDB
 ↓
Concurrent AI Calls
 ↓
Ordered Responses
 ↓
MongoDB History
 ↓
React
```

---

## 18. Design Decisions

### MongoDB Prompt Storage

Prompt templates are stored in MongoDB instead of being hard-coded in API routes.

This separates prompt data from application logic and makes prompt management more flexible.

### Service Layer

The backend separates responsibilities:

```text
Routes
  ↓
Services
  ↓
Database
```

This improves maintainability and testability.

### ThreadPoolExecutor

`ThreadPoolExecutor` is used for concurrent batch processing because AI/API calls are I/O-bound.

### Mock AI Service

A mock AI service allows the project to run without requiring a paid AI API.

The AI logic is isolated in `ai_service.py`, making it easier to replace the mock implementation with a real provider.

### Batch Size Limit

The batch API is limited to 10 questions to prevent uncontrolled resource usage.

### Response Ordering

The application explicitly preserves original input order even though AI calls execute concurrently.

---

## 19. Limitations

- The current implementation uses a mock AI service.
- No authentication or authorization is implemented.
- Prompt selection currently uses `Education_Prompt`.
- No API rate limiting is implemented.
- No history dashboard is currently available.
- No pagination API for history is implemented.
- The application is primarily designed for the assessment/demo environment.
- Production monitoring and advanced observability are not implemented.

---

## 20. Future Improvements

Potential improvements include:

- Integrate OpenAI or another production LLM provider.
- Add authentication and authorization.
- Add API rate limiting.
- Add structured logging.
- Add request IDs.
- Add retry mechanisms for temporary AI failures.
- Add MongoDB indexes for history queries.
- Add history pagination and filtering.
- Add a frontend history dashboard.
- Support multiple prompt templates.
- Add Docker support.
- Add CI/CD using GitHub Actions.
- Add production monitoring and metrics.
- Add comprehensive integration and load testing.

---

## License

This project was developed as part of a Full Stack Developer assessment.
