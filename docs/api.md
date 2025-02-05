## Math Query API

## Overview
This API exposes an endpoint for querying the **Local RAG system**, which retrieves mathematical knowledge from uploaded documents. The API runs on **port 8000** in a separate thread alongside the **Streamlit UI**.

## Initialization Sequence
1. **Start the Streamlit UI**.
2. **Upload documents** through the UI.
3. The **RAG pipeline initializes** and creates an indexed knowledge base.
4. **API endpoints become available** on `http://localhost:8000/api/`.

## API Endpoints

### **POST `/api/math-query`**
#### **Description**:
Accepts a **math-related query** (including LaTeX expressions) and returns a response with relevant references.

#### **Request Example (cURL)**
```json
curl -X POST "http://localhost:8000/api/math-query" \
-H "Content-Type: application/json" \
-d '{ 
    "question": "What is the formula for Bayes'\'' theorem?" 
    }' | python -m json.tool

```

### Response Example
```json
{
    "response": "The formula for Bayes' theorem can be expressed as P(A|B) = P(B|A) * P(A) / P(B)...",
    "references": [
        {
            "file_name": "math_textbook.pdf",
            "page": 42,
            "text": "Total Probability Theorem and Bayes ’Rule...",
            "score": 0.78
        }
    ]
}ß
```

### Error States
#### Implemented
- `500 Internal Server Error`: Query engine not initialized
- `503 Processing Error`: Query processing error

#### Not Yet Implemented
- `400 Bad Request`: Invalid request format
- `408 Request Timeout`: Query processing took too long
- `429 Too Many Requests`: Rate limit exceeded
- `502 Bad Gateway`: API server is down
