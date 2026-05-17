# Approach Document — SHL Conversational Assessment Recommender

**Name:** Shahid Khan  
**GitHub:** https://github.com/shahidk07/assessment_agent_rag
## Overview

The goal of this project was to build a conversational AI agent capable of recommending SHL assessments through natural dialogue instead of traditional keyword-based search.

The system was designed as a Retrieval-Augmented Generation (RAG) application where:

* semantic retrieval handles grounding,
* the LLM handles conversational reasoning,
* and the frontend handles structured presentation.

The assistant supports:

* clarification for vague queries,
* conversational refinement,
* grounded recommendations,
* assessment comparison,
* and off-topic refusal behavior.

The backend was implemented using FastAPI and deployed on Render.

---

# System Design

## Architecture

```text
User Query
    ↓
Frontend Chat UI
    ↓
FastAPI Backend
    ↓
Conversation Controller
    ↓
Hybrid Intent Routing
    ↓
Retrieval System
    ↓
FAISS + SHL Dataset
    ↓
LLM Response Generation
    ↓
Structured Recommendations
```

The system separates responsibilities into multiple layers:

### Retrieval Layer

Responsible for:

* semantic search,
* threshold filtering,
* metadata lookup,
* and recommendation grounding.

### LLM Layer

Responsible for:

* conversational reasoning,
* clarification generation,
* comparison summaries,
* and recruiter-friendly explanations.

### Frontend Layer

Responsible for:

* conversational UI,
* recommendation cards,
* comparison rendering,
* and recruiter interaction flow.

---

# Retrieval Setup

The SHL catalog was scraped and stored locally as structured JSON data.

Semantic retrieval was implemented using:

* Sentence Transformers (`all-MiniLM-L6-v2`)
* FAISS vector search

The retrieval workflow:

```text
User Query
    ↓
Query Embedding
    ↓
FAISS Similarity Search
    ↓
Threshold Filtering
    ↓
Lightweight Reranking
    ↓
Top Assessments
```

To improve retrieval quality:

* weak semantic matches were filtered using thresholds,
* lightweight reranking was introduced,
* and exact metadata lookup was added for direct assessment queries.

This reduced noisy recommendations and improved conversational grounding.

---

# Prompt Design

The prompts were designed to keep the assistant:

* recruiter-focused,
* conversational,
* grounded to retrieved data,
* and resistant to hallucination.

The prompts instructed the model to:

* avoid inventing assessments,
* explain recommendations naturally,
* ask clarification questions when context is insufficient,
* and produce concise recruiter-oriented responses.

Comparison prompts were designed separately to generate grounded comparison summaries using retrieved SHL metadata.

---

# Intent Routing

Initially, the project relied entirely on LLM-based intent classification.

However, short recruiter queries such as:

* “intern”
* “developer”
* “machine learning”

were inconsistently classified.

To improve conversational stability, the system evolved into a hybrid routing architecture combining:

* lightweight rule-based routing,
* keyword heuristics,
* and LLM fallback classification.

This improved:

* response consistency,
* latency,
* and conversational reliability.

---

# Frontend Design

The frontend was intentionally kept lightweight using:

* HTML,
* CSS,
* JavaScript,
* jQuery,
* and Tailwind CSS.

Recommendations and comparisons were displayed using structured cards instead of raw conversational text.

This improved:

* readability,
* conversational clarity,
* and recruiter experience.

The frontend and backend were ultimately served through the same FastAPI application using:

* `StaticFiles`
* and `FileResponse`

which simplified deployment and routing.

---

# Evaluation Approach

The system was tested iteratively using realistic conversational flows.

Testing focused on:

* vague recruiter queries,
* conversational refinements,
* recommendation grounding,
* comparison handling,
* frontend rendering,
* deployment consistency,
* and off-topic refusal behavior.

The architecture evolved significantly through debugging and iterative testing rather than following a perfectly fixed design from the beginning.

---

# What Did Not Work Initially

Several early approaches produced poor conversational quality.

### Pure LLM Intent Classification

Fully LLM-based intent routing caused inconsistent conversational behavior for short recruiter inputs.

### Dense Conversational Responses

Early responses were:

* repetitive,
* robotic,
* and metadata-heavy.

This reduced conversational quality.

### Weak Semantic Retrieval

Semantic retrieval occasionally returned broad graduate assessments instead of domain-specific assessments.

Threshold filtering and lightweight reranking were later introduced to improve retrieval quality.

---

# AI Tools Used

The project used AI-assisted development tools for:

* brainstorming architecture ideas,
* refining prompts,
* debugging conversational flows,
* improving frontend rendering,
* and optimizing deployment setup.

However, the implementation, debugging decisions, retrieval architecture, routing logic, and deployment integration were manually developed and iteratively refined during the project.

---

# Conclusion

This project evolved from a simple prompt-based chatbot into a retrieval-augmented conversational AI application capable of:

* grounded SHL assessment recommendations,
* conversational clarification,
* refinement handling,
* comparison support,
* and recruiter-oriented interaction.

The project emphasized:

* AI engineering,
* conversational orchestration,
* retrieval grounding,
* deployment architecture,
* and practical GenAI application design.
