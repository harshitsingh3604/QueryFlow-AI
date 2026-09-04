# QueryFlow AI

A full-stack AI question-answering application built for the Intucate Full Stack Developer case study.

The application provides:

- A Flask REST API for single questions.
- A Flask REST API for batch questions.
- MongoDB-backed prompt templates.
- Google Gemini API integration for AI responses.
- MongoDB history persistence.
- Concurrent batch processing while preserving the original input order.
- A React + Vite frontend for consuming both APIs.
- Request validation and JSON error handling.
- Automated backend tests with pytest.

---

## 1. Technology Stack

### Backend

- Python 3.10+
- Flask
- Flask-CORS
- PyMongo
- python-dotenv
- Google GenAI Python SDK (`google-genai`)
- pytest

### Database

- MongoDB / MongoDB Atlas

### AI Provider

- Google Gemini API
- Current configured model: `gemini-3.6-flash`

### Frontend

- React
- Vite
- React Markdown

---

## 2. Project Structure

```text
QueryFlow-AI/
│
├── README.md
├── REQUIREMENTS.md
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── database/
│   │   │   └── mongodb.py
│   │   │
│   │   ├── routes/
│   │   │   └── ai_routes.py
│   │   │
│   │   └── services/
│   │       ├── ai_service.py
│   │       ├── history_service.py
│   │       └── prompt_service.py
│   │
│   ├── scripts/
│   │   └── seed_database.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_ask.py
│   │   ├── test_batch.py
│   │   └── test_health.py
│   │
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   └── run.py
│
└── frontend/
    ├── public/
    │   └── favicon.ico
    │
    ├── src/
    │   ├── assets/
    │   ├── App.css
    │   ├── App.jsx
    │   ├── index.css
    │   └── main.jsx
    │
    ├── .env.example
    ├── .gitignore
    ├── eslint.config.js
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── README.md
    └── vite.config.js
```

---

## 3. Architecture

The backend separates HTTP handling, business logic, database access, and AI communication.

```text
React Frontend
      │
      │ HTTP / JSON
      ▼
Flask Routes
      │
      ├──────────────► Prompt Service
      │                    │
      │                    ▼
      │                 MongoDB
      │
      ├──────────────► AI Service
      │                    │
      │                    ▼
      │               Gemini API
      │
      └──────────────► History Service
                           │
                           ▼
                        MongoDB
```

### Responsibilities

**Routes**

- Validate HTTP requests.
- Call the required services.
- Return JSON responses and HTTP status codes.

**Prompt Service**

- Retrieve the `Education_Prompt` template from MongoDB.
- Validate the template.
- Replace `{{userInput}}` with the user's question.

**AI Service**

- Communicate with Google Gemini.
- Retry temporary Gemini availability errors.
- Process batch requests concurrently using `ThreadPoolExecutor`.
- Preserve the original input order.

**History Service**

- Store each interaction in MongoDB.

**Database Module**

- Create and reuse the MongoDB client.
- Provide access to the `prompts` and `history` collections.

---

## 4. Prerequisites

Install the following before running the project:

- Python 3.10 or newer
- Node.js and npm
- MongoDB, or a MongoDB Atlas account
- A Google Gemini API key

---

## 5. MongoDB Setup

The application uses two MongoDB collections:

```text
prompts
history
```

### Prompts collection

The application expects a prompt document with:

```json
{
  "_id": "Education_Prompt",
  "template": "You are an expert in education domain. Answer the following: {{userInput}}"
}
```

The template is retrieved from MongoDB at runtime. It is not hard-coded inside the API routes.

### History collection

The `history` collection stores each AI interaction.

A successful record contains fields similar to:

```json
{
  "promptId": "Education_Prompt",
  "userInput": "What is Python?",
  "prompt": "You are an expert in education domain. Answer the following: What is Python?",
  "response": "Python is ...",
  "createdAt": "..."
}
```

For an individual AI failure during batch processing, the history record can additionally contain an `error` field.

### Seed the prompt

The repository includes a seed script:

```bash
cd backend
python scripts/seed_database.py
```

The script creates or updates the `Education_Prompt` document.

---

## 6. Environment Configuration

Sensitive values are loaded from environment variables.

### Backend

Create:

```text
backend/.env
```

Use the following format:

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=your_database_name
GEMINI_API_KEY=your_gemini_api_key
```

An example file is provided at:

```text
backend/.env.example
```

### Frontend

Create:

```text
frontend/.env
```

Use:

```env
VITE_API_BASE_URL=http://localhost:5000
```

An example is provided at:

```text
frontend/.env.example
```

### Security

Do not commit the real `.env` files.

Never place the Gemini API key in React/frontend source code.

The intended flow is:

```text
Browser
   │
   ▼
Flask Backend
   │
   ▼
Gemini API
```

The Gemini API key remains on the backend.

---

## 7. Backend Installation

From the project root:

```bash
cd backend
```

Create and activate a virtual environment if desired.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 8. Start the Backend

From the `backend` directory:

```bash
python run.py
```

The Flask application runs on:

```text
http://127.0.0.1:5000
```

The frontend is configured to communicate with:

```text
http://localhost:5000
```

Make sure the backend is running before using the frontend.

---

## 9. Health Check

The application provides:

```http
GET /health
```

Example:

```text
http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

# 10. API — Single Question

## Endpoint

```http
POST /ask
```

### Request

Content-Type:

```text
application/json
```

Example:

```json
{
  "userInput": "What is Python?"
}
```

### Processing flow

```text
Client
  ↓
Validate userInput
  ↓
Retrieve Education_Prompt from MongoDB
  ↓
Replace {{userInput}}
  ↓
Send final prompt to Gemini
  ↓
Receive AI response
  ↓
Save interaction to history
  ↓
Return JSON
```

### Example final prompt

If the MongoDB template is:

```text
You are an expert in education domain. Answer the following: {{userInput}}
```

and the user sends:

```text
What is Python?
```

the generated prompt becomes:

```text
You are an expert in education domain. Answer the following: What is Python?
```

### Response

```json
{
  "response": "Python is a high-level, general-purpose programming language..."
}
```

---

# 11. API — Batch Questions

## Endpoint

```http
POST /ask/batch
```

### Request

```json
{
  "userInputs": [
    "What is Python?",
    "What is Flask?",
    "What is MongoDB?"
  ]
}
```

### Processing

The prompt template is retrieved once and used to build a prompt for each question.

The AI requests are then submitted concurrently using `ThreadPoolExecutor`.

```text
Question 1 ──┐
Question 2 ──┼──► Concurrent Gemini requests
Question 3 ──┘
```

The backend uses a maximum of three concurrent Gemini requests at a time.

### Response ordering

Requests can finish in a different order:

```text
Question 2
Question 3
Question 1
```

but the returned responses remain associated with their original inputs:

```json
{
  "responses": [
    {
      "userInput": "What is Python?",
      "response": "..."
    },
    {
      "userInput": "What is Flask?",
      "response": "..."
    },
    {
      "userInput": "What is MongoDB?",
      "response": "..."
    }
  ]
}
```

The implementation uses the original input index to restore ordering after concurrent execution.

### Batch limit

The API accepts a maximum of:

```text
10 questions
```

A request containing more than 10 questions returns HTTP `400`.

---

# 12. Validation

The APIs validate incoming JSON requests.

### Single API

The following are rejected:

- Missing request body
- Non-JSON request body
- Missing `userInput`
- Empty `userInput`
- Whitespace-only `userInput`
- Non-string `userInput`

### Batch API

The following are rejected:

- Missing request body
- Non-JSON request body
- Missing `userInputs`
- `userInputs` not being an array
- Empty `userInputs`
- More than 10 questions
- Empty question items
- Non-string question items

Invalid requests return JSON error responses with HTTP `400`.

---

# 13. Error Handling

The backend handles:

- Invalid client input
- MongoDB failures
- Missing prompt templates
- AI/Gemini failures
- History persistence failures
- Unexpected server errors

Examples:

### Invalid input

```json
{
  "error": "userInput is required and must be a non-empty string"
}
```

### Prompt not found

```json
{
  "error": "Prompt 'Education_Prompt' not found"
}
```

### AI failure

```json
{
  "error": "AI service is unavailable"
}
```

### History persistence failure

```json
{
  "error": "Failed to save request history"
}
```

Internal stack traces are not returned to API clients.

---

# 14. Gemini Integration

The project uses the official Google GenAI Python SDK.

The Gemini integration is isolated in:

```text
backend/app/services/ai_service.py
```

The API key is loaded from:

```env
GEMINI_API_KEY=...
```

The configured model is:

```text
gemini-3.6-flash
```

The service calls Gemini with the final prompt generated from the MongoDB template.

The service also retries temporary Gemini availability errors before returning an AI failure.

---

# 15. Frontend

The frontend is a React + Vite application.

It provides:

### Single Question

- Text input
- Validation
- Loading state
- API request
- Error state
- Markdown-formatted AI response

### Batch Questions

- Multiple question inputs
- Add/remove question controls
- Maximum of 10 questions
- Loading state
- Error handling
- AI response display
- Responses displayed in original input order

Gemini responses can contain Markdown such as:

```text
**important**

- Point one
- Point two
```

The frontend uses `react-markdown` to render this formatting.

---

# 16. Run the Frontend

Open a second terminal.

From the project root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Make sure `frontend/.env` contains:

```env
VITE_API_BASE_URL=http://localhost:5000
```

Start the development server:

```bash
npm run dev
```

Vite will provide a local URL, normally:

```text
http://localhost:5173
```

Open that URL in the browser.

---

# 17. Testing

The backend uses `pytest`.

From the backend directory:

```bash
python -m pytest -q
```

The test suite covers:

### Health

- Health endpoint

### Single API

- Valid request
- Missing input
- Empty input
- Invalid input type
- AI failure
- Database failure

### Batch API

- Valid batch
- Empty batch
- Missing `userInputs`
- Invalid `userInputs` type
- Invalid batch item
- Response count
- Response ordering
- AI failure handling
- Database failure
- Maximum batch size
- Invalid JSON body
- Prompt not found
- History persistence
- Concurrent execution/order behavior

The concurrency test uses controlled completion delays to verify that results remain in the original order even when requests finish at different times.

---

# 18. Manual API Testing

The APIs can be tested with Thunder Client, Postman, curl, or another REST client.

### Single request

```http
POST http://127.0.0.1:5000/ask
Content-Type: application/json
```

```json
{
  "userInput": "Explain polymorphism in Java."
}
```

### Batch request

```http
POST http://127.0.0.1:5000/ask/batch
Content-Type: application/json
```

```json
{
  "userInputs": [
    "What is Python?",
    "What is Flask?",
    "What is MongoDB?"
  ]
}
```

---

# 19. End-to-End Flow

## Single Question

```text
React
  │
  │ POST /ask
  ▼
Flask
  │
  ├── Validate input
  │
  ├── Retrieve Education_Prompt
  │        │
  │        ▼
  │     MongoDB
  │
  ├── Build final prompt
  │
  ├── Gemini API
  │        │
  │        ▼
  │     AI response
  │
  ├── Save history
  │        │
  │        ▼
  │     MongoDB
  │
  ▼
JSON response
  │
  ▼
React
```

## Batch

```text
React
  │
  │ POST /ask/batch
  ▼
Flask
  │
  ├── Validate all inputs
  │
  ├── Retrieve prompt once
  │
  ├── Build prompts
  │
  ├── ThreadPoolExecutor
  │       ├── Gemini request 1
  │       ├── Gemini request 2
  │       └── Gemini request 3
  │
  ├── Restore original input order
  │
  ├── Save each result to history
  │
  ▼
JSON response
  │
  ▼
React
```

---

# 20. Configuration and Security Notes

- Never commit `backend/.env`.
- Never commit `frontend/.env`.
- Never put `GEMINI_API_KEY` in frontend code.
- Use `.env.example` files as configuration templates.
- Keep MongoDB credentials in environment variables.
- Do not commit API keys to GitHub.

---

# 21. Design Decisions

### MongoDB Prompt Storage

The prompt template is retrieved from MongoDB rather than being hard-coded in the API route. This keeps prompt data separate from HTTP/business logic.

### Service Layer

The project separates:

```text
Routes
Services
Database
AI Provider
```

This makes the application easier to maintain and test.

### Gemini Service

Gemini-specific code is isolated in `ai_service.py`. This prevents the Flask routes from being tightly coupled to the AI provider.

### Concurrent Batch Processing

`ThreadPoolExecutor` is used because calls to the external Gemini API are I/O-bound. Multiple requests can be in progress at the same time without unnecessarily processing the entire batch sequentially.

### Response Ordering

Each prompt is associated with its original index. Results are placed back into that index so concurrent completion does not change the API response order.

### Batch Size

The batch API is limited to 10 questions to avoid uncontrolled resource usage.

### Markdown Responses

Gemini can return Markdown. The React frontend uses `react-markdown` so headings, lists, bold text, and other supported Markdown formatting are rendered properly.

---

# 22. Limitations

- Authentication and authorization are not implemented.
- API rate limiting is not implemented.
- Prompt selection currently uses `Education_Prompt`.
- There is no frontend history dashboard.
- There is no history pagination/filtering API.
- Production monitoring and advanced observability are not implemented.
- The application is primarily intended for the assessment/demo environment.

---

# 23. Possible Future Improvements

- Add authentication and authorization.
- Add API rate limiting.
- Add structured logging and request IDs.
- Add retry/backoff handling for additional transient AI errors.
- Add MongoDB indexes for history queries.
- Add history pagination and filtering.
- Add a frontend history dashboard.
- Support multiple prompt templates.
- Add Docker support.
- Add CI/CD.
- Add integration and load testing.
- Add production monitoring and metrics.

---

## 24. Assessment Requirement Mapping

| Assessment Requirement | Implementation |
|---|---|
| Python + Flask backend | `backend/` |
| MongoDB | `backend/app/database/mongodb.py` |
| Prompt collection | `prompts` collection |
| `Education_Prompt` | `backend/scripts/seed_database.py` |
| `{{userInput}}` replacement | `prompt_service.py` |
| AI response | `ai_service.py` using Gemini |
| History persistence | `history_service.py` |
| Single API | `POST /ask` |
| Batch API | `POST /ask/batch` |
| Concurrent processing | `ThreadPoolExecutor` |
| Original response order | Indexed result collection |
| Input validation | `ai_routes.py` |
| JSON error handling | `ai_routes.py` |
| Frontend client | `frontend/` |
| Single question UI | `frontend/src/App.jsx` |
| Batch question UI | `frontend/src/App.jsx` |
| Loading/error states | `frontend/src/App.jsx` |
| Markdown response rendering | `react-markdown` |
| Automated tests | `backend/tests/` |
| Environment configuration | `.env.example` files |
| Secret protection | `.gitignore` |

---

## 25. Quick Start

### Terminal 1 — Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/seed_database.py
python run.py
```

### Terminal 2 — Frontend

```powershell
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

## License

This project was developed as part of the Intucate Full Stack Developer assessment.
