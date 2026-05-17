# SHL Conversational Assessment Recommender

## Project Documentation

---

# 1. Introduction

## Project Overview

This project is a conversational AI recommendation system designed for recruiters and hiring managers.

The system helps users discover suitable SHL assessments through natural conversation instead of traditional keyword-based search systems.

Recruiters often do not know exact SHL terminology or assessment names. Instead of manually browsing the catalog, they can simply describe their hiring requirements in plain English.

Example:

> "I am hiring a mid-level Java developer who communicates with stakeholders."

The assistant:
- understands hiring intent,
- asks clarification questions,
- retrieves relevant SHL assessments,
- supports conversational refinement,
- compares assessments,
- and generates grounded recruiter-focused responses.

The assistant only recommends assessments from the SHL catalog.

---

# 2. Core Objectives

The system should:

- Support conversational interaction
- Ask clarification questions for vague queries
- Recommend between 1–10 SHL assessments
- Compare assessments using catalog data
- Handle recommendation refinements
- Prevent hallucinations
- Stay restricted to SHL catalog knowledge
- Return structured API responses

---

# 3. High-Level Architecture

```text
Recruiter Query
      ↓
Frontend Chat Interface
      ↓
FastAPI Backend
      ↓
Conversation Controller
      ↓
Hybrid Intent Routing
      ↓
Retrieval + LLM System
      ↓
FAISS + SHL Dataset
      ↓
Grounded Conversational Response
      ↓
Recommendation Cards
```

---

# 4. Technology Stack

## Backend
- Python
- FastAPI
- Uvicorn

## AI / LLM
- Groq API
- Llama 3.1 8B Instant

## Retrieval
- Sentence Transformers
- FAISS
- NumPy

## Frontend
- HTML
- CSS
- JavaScript
- jQuery
- Tailwind CSS

## Deployment
- Render

---
# 4.1. Project Structure

```text
.
├── app
│   ├── data
│   │   ├── assessments.json
│   │   ├── cleaned_assessments.json
│   │   ├── detailed_assessments.json
│   │   └── faiss_index
│   │       ├── metadata.pkl
│   │       └── shl_index.faiss
│   │
│   ├── main.py
│   │
│   ├── routes
│   │   └── chat.py
│   │
│   ├── scraper
│   │   ├── outer_scrapper.py
│   │   └── scrape_shl.py
│   │
│   ├── services
│   │   ├── create_embeddings.py
│   │   ├── llm_service.py
│   │   ├── recommendation_service.py
│   │   └── retrieval_service.py
│   │
│   └── utils
│       └── clean_data.py
│
├── frontend
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── README.md
├── render.yaml
├── requirements.txt
└── runtime.txt
```

# 5. Retrieval Architecture

## Objective

Retrieve relevant SHL assessments using semantic vector similarity.

---

## Retrieval Workflow

```text
User Query
     ↓
Generate Query Embedding
     ↓
FAISS Similarity Search
     ↓
Threshold Filtering
     ↓
Lightweight Reranking
     ↓
Top Relevant Assessments
```

---

## Retrieval Features

The retrieval system includes:
- semantic vector retrieval,
- threshold filtering,
- lightweight reranking,
- exact metadata lookup,
- and grounded recommendation generation.

---

## Threshold Filtering

Weak semantic matches are filtered using similarity thresholds.

This helps reduce:
- noisy recommendations,
- weak semantic matches,
- and irrelevant retrievals.

---

## Lightweight Reranking

Keyword-based reranking is applied after FAISS retrieval.

Example:
- boosting developer-related assessments for technical hiring,
- boosting manager-related assessments for leadership roles,
- improving internship recommendation relevance.

---

# 6. LLM Integration

## Objective

Use an LLM for conversational reasoning and grounded response generation.

The retrieval system provides grounded SHL assessment data while the LLM focuses on:
- conversational explanations,
- clarification generation,
- comparison summaries,
- and recruiter-friendly responses.

---

## Technologies Used

- Groq API
- Llama 3.1 8B Instant

---

## Responsibilities of the LLM

The LLM is responsible for:
- natural language understanding,
- conversational reasoning,
- clarification generation,
- recommendation explanation,
- comparison summaries,
- and conversational flow.

The LLM does not invent assessments independently.

All recommendations are grounded through retrieved SHL catalog data.

---

# 7. FastAPI Backend Development

## API Endpoints

### GET /health

```json
{
  "status": "ok"
}
```

---

### POST /chat

The backend accepts:

```json
{
  "messages": []
}
```

and returns:
- conversational replies,
- structured recommendations,
- comparison data,
- and conversation status.

---

## Stateless Architecture

The backend stores no persistent conversation memory.

Each API request contains:

```json
messages[]
```

This keeps the architecture:
- evaluator-compliant,
- scalable,
- and deployment-friendly.

---

# 8. Hybrid Intent Classification

## Objective

Classify recruiter queries into conversational intents.

---

## Intent Classification Flow

```text
User Query
    ↓
Rule-Based Routing
    ↓
LLM Fallback Classification
    ↓
Conversation Controller
    ↓
Appropriate Response Flow
```

---

## Supported Intents

- greeting
- vague
- recommendation
- comparison
- lookup
- off-topic

---

## Why Hybrid Classification Was Used

Initially, the system relied entirely on LLM-based zero-shot intent classification.

However, short recruiter queries such as:
- "intern"
- "developer"
- "machine learning"

were inconsistently classified.

To improve:
- routing consistency,
- response stability,
- and conversational flow,

the architecture evolved into a hybrid system combining:
- lightweight rule-based routing,
- keyword heuristics,
- and LLM fallback classification.

---

# 9. Conversation Logic

## Clarification Logic

The assistant asks clarification questions for vague recruiter queries.

Example:

### User

> "I need an assessment"

### Assistant

> "Could you share more details about the role, seniority level, or skills you are hiring for?"

---

## Recommendation Logic

Once sufficient context exists:
- the retriever fetches relevant SHL assessments,
- the LLM generates recruiter-friendly explanations,
- and recommendation cards are rendered separately.

---

## Comparison Logic

The assistant supports grounded comparison responses using retrieved SHL catalog data.

Example:

> "Compare OPQ and GSA"

The system:
- retrieves relevant assessments,
- generates comparison reasoning,
- and displays structured comparison cards.

---

## Refusal Logic

The assistant refuses:
- non-SHL recommendations,
- unrelated hiring advice,
- and unsafe/off-topic prompts.

---

# 10. Frontend Development

## Technologies Used

- HTML
- CSS
- JavaScript
- jQuery
- Tailwind CSS

---

## Frontend Features

The frontend supports:
- conversational interaction,
- recommendation cards,
- comparison cards,
- loading states,
- conversational history,
- and API integration.

---

## Recommendation Cards

Recommendations are rendered as structured frontend cards containing:
- assessment titles,
- durations,
- SHL URLs,
- and PDF links.

This allows the conversational response to focus on:
- recruiter reasoning,
- hiring context,
- and recommendation guidance.

---

## Comparison UI

Comparison responses use structured comparison cards for:
- cleaner readability,
- recruiter-friendly interaction,
- and improved conversational presentation.

---

# 11. UI Adjustments & Conversational Improvements

## Objective

Improve recruiter experience and conversational presentation quality.

---

## Conversational Response Improvements

Early conversational responses felt:
- repetitive,
- robotic,
- and metadata-heavy.

The prompts were redesigned to:
- reduce robotic phrasing,
- improve recruiter-oriented explanations,
- avoid title dumping,
- and improve conversational readability.

---

## Frontend Rendering Improvements

Initially, long LLM-generated responses appeared as dense paragraph blocks.

Frontend rendering was improved by:
- preserving line breaks,
- improving spacing,
- separating recommendation cards from explanations,
- and structuring conversational output more clearly.

---

## Recommendation & Comparison Presentation

The UI was adjusted to:
- render recommendation cards separately,
- render comparison cards separately,
- reduce conversational clutter,
- and improve recruiter readability.

This separation allowed:
- the frontend to focus on structured metadata rendering,
- while the LLM focused on conversational reasoning.

---

# 12. Deployment

## Deployment Platform

- Render

---

## Deployment Architecture

Frontend and backend are served through the same FastAPI application.

FastAPI StaticFiles and FileResponse are used to:
- serve frontend assets,
- render the frontend UI,
- and simplify deployment routing.

---

## Relative API Routing

The frontend communicates with the backend using:

```javascript
/chat
```

instead of localhost URLs.

This ensures:
- deployment compatibility,
- local execution consistency,
- and simpler environment management.

---

# 13. Documentation

## Objective

Document:
- system architecture,
- conversational orchestration,
- retrieval strategy,
- deployment structure,
- engineering decisions,
- and implementation workflow.

---

## Key Areas Covered

### Retrieval Architecture
- semantic vector retrieval,
- threshold filtering,
- reranking,
- and metadata lookup.

### Conversational Architecture
- hybrid intent routing,
- clarification logic,
- recommendation generation,
- and grounded conversational responses.

### Frontend Architecture
- conversational UI,
- recommendation cards,
- comparison cards,
- and recruiter-focused interaction flow.

### Deployment Architecture
- FastAPI static file serving,
- frontend/backend integration,
- and Render deployment workflow.

---

# 14. Engineering Learnings

One of the biggest learnings during development was understanding that conversational AI engineering involves much more than prompt engineering alone.

The project required:
- retrieval engineering,
- conversational orchestration,
- frontend/backend integration,
- deployment architecture,
- semantic search optimization,
- and grounded AI response generation.

The system evolved from a simple prompt-based chatbot into a retrieval-augmented conversational AI application with recruiter-focused conversational design.
