# QueryFlow - AI

# Requirements Specification

## 1. Objective

Build a backend application using Python and Flask that accepts user questions, retrieves a prompt template from MongoDB, generates an AI response, stores the interaction in MongoDB, and returns the response through a REST API.

The application must also support processing multiple user questions concurrently/asynchronously while preserving the original input order in the final response.

---

## 2. Technology Requirements

### Backend

- Python
- Flask

### Database

- MongoDB

### AI

- OpenAI API(Optional)
- A mock AI service or another permitted AI solution may be used.

### Frontend

- A frontend client will be built to demonstrate and consume
  the backend APIs.
- The frontend is not allowed to replace or change the required
  backend functionality.

---

## 3. API #1 — Single Question

### Endpoint

POST 

### Purpose

Accept one user question and generate an AI response.

### Request

Content-Type: application/json

{
"userInput": "How much should I score in each subject to pass CA final?"
}

### Processing Flow

1. Receive the request.
2. Validate `userInput`.
3. Retrieve the required prompt template from MongoDB.
4. Replace `{{userInput}}` in the template with the user's input.
5. Send the resulting prompt to the AI service.
6. Receive the AI response.
7. Store the request and response in MongoDB.
8. Return the response to the client.

### Example Prompt

MongoDB:

{
"\_id": "Education_Prompt",
"template": "You are an expert in education domain. Answer the following: {{userInput}}"
}

User input:

"How much should I score in each subject to pass CA final?"

Final prompt:

"You are an expert in education domain. Answer the following:
How much should I score in each subject to pass CA final?"

### Response

{
"response": "..."
}

---

## 4. MongoDB — Prompts Collection

Collection name:

prompts

The collection must contain the prompt template required by
the application.

Example:

{
"\_id": "Education_Prompt",
"template": "You are an expert in education domain. Answer the following: {{userInput}}"
}

The prompt must be retrieved from MongoDB rather than being
hard-coded inside the API route.

---

## 5. MongoDB — History Collection

Collection name:

history

Every AI interaction must be stored.

The stored information should include the relevant request,
generated prompt, AI response, and timestamp.

Example:

{
"userInput": "What is Python?",
"prompt": "You are an expert in education domain. Answer the following: What is Python?",
"response": "...",
"createdAt": "..."
}

---

## 6. API #2 — Multiple Questions

A second POST API must accept multiple user questions.

Example:

POST /ask/batch

Request:

{
"userInputs": [
"What is Python?",
"What is Flask?",
"What is MongoDB?"
]
}

The exact endpoint naming may be adjusted if the case study
specifies another name, but the required functionality must
remain unchanged.

---

## 7. Asynchronous / Concurrent Processing

The batch API must process multiple AI requests
asynchronously/concurrently.

The implementation must NOT unnecessarily process every
question one after another.

Conceptually:

Question 1 ──┐
Question 2 ──┼──> Concurrent AI processing
Question 3 ──┘

The implementation should allow multiple AI requests to be
in progress at the same time.

---

## 8. Response Ordering

Although requests may complete at different times, the final
responses MUST be returned in the same order as the original
inputs.

Input:

[
"Question A",
"Question B",
"Question C"
]

Even if processing completes in this order:

B
C
A

The API must return:

[
"Response A",
"Response B",
"Response C"
]

Therefore, asynchronous processing must not change the
relationship between each input and its corresponding response.

---

## 9. Validation

The APIs should validate incoming requests.

At minimum, handle:

- Missing request body
- Missing `userInput`
- Empty `userInput`
- Incorrect data type
- Missing `userInputs`
- Empty `userInputs`
- Invalid batch input

Invalid requests should return meaningful JSON error messages
and appropriate HTTP status codes.

---

## 10. Error Handling

The application should gracefully handle failures such as:

- MongoDB connection/database errors
- Prompt not found
- AI service failure
- Invalid client input
- Unexpected server errors

The API should return clean JSON error responses rather than
exposing internal stack traces to the client.

---

## 11. Persistence

Successful AI interactions must be persisted in MongoDB.

The system should ensure that the relevant input, generated
prompt, response, and timestamp can be retrieved from the
history collection.

---

## 12. Backend Architecture

The backend should separate responsibilities.

Suggested logical structure:

Routes
↓
Services
↓
Database / AI Provider

Routes should handle HTTP concerns.

Services should contain business logic.

Database code should handle MongoDB operations.

AI service should handle communication with the AI provider.

---

## 13. Frontend

A simple frontend client will be developed to demonstrate
the APIs.

The frontend should provide:

- Single-question input
- Batch-question input
- API request handling
- Loading state
- Error state
- Response display
- Batch responses displayed in original order

The frontend should remain simple and should not take priority
over the required backend functionality.

---

## 14. Security / Configuration

Sensitive values such as:

- MongoDB connection string
- AI API key

must not be hard-coded into source code.

Environment variables should be used.

The `.env` file must not be committed to Git.

An `.env.example` file should be provided.

---

## 15. Testing Requirements

The implementation should be tested for:

### Single API

- Valid request
- Missing input
- Empty input
- Invalid input
- AI failure
- Database failure

### Batch API

- Valid batch
- Single item batch
- Multiple items
- Empty batch
- Invalid batch
- AI failure
- Response ordering
- Concurrent execution

---

## 16. Definition of Done

The project will be considered functionally complete when:

[ ] Flask application runs successfully.

[ ] MongoDB connection works.

[ ] `prompts` collection exists.

[ ] Prompt template can be retrieved from MongoDB.

[ ] `POST /ask` works.

[ ] User input is inserted into the prompt template.

[ ] AI/mock AI response is generated.

[ ] Interaction is saved in `history`.

[ ] Single API returns JSON response.

[ ] Batch API exists.

[ ] Batch requests are processed concurrently/asynchronously.

[ ] Batch responses maintain original input order.

[ ] Validation is implemented.

[ ] Error handling is implemented.

[ ] APIs are tested.

[ ] Frontend can consume the APIs.

[ ] No secrets are committed.

[ ] README explains setup and execution.
