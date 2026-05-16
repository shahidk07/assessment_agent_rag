from app.services.llm_service import (
    generate_response,
    client
)

import pickle
from app.services.retrieval_service import (
    retrieve_assessments
)

with open(
    "app/data/faiss_index/metadata.pkl",
    "rb"
) as f:

    metadata = pickle.load(f)

# -----------------------------
# INTENT CLASSIFICATION
# -----------------------------

def classify_query(latest_query):

    prompt = f"""
    You are an intent classification system.

    Classify the user query into ONLY ONE category.

    Categories:
    - lookup
    - greeting
    - vague
    - recommendation
    - comparison
    - off-topic

    Rules:
    
    greeting:
    greetings like hi, hello, hey, good morning
    
    
    lookup:
    requests asking for:
    - assessment link
    - download link
    - PDF
    - exact assessment lookup
    vague:
    hiring-related but lacks enough details

    recommendation:
    clear hiring or assessment request

    comparison:
    comparing two assessments

    off-topic:
    unrelated to SHL hiring assessments

    Return ONLY the category name.

    User Query:
    {latest_query}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    intent = response.choices[0].message.content.strip().lower()

    return intent


# -----------------------------
# GREETING RESPONSE
# -----------------------------

def greeting_response():

    return {
        "reply": (
            "Hello! I can help you find suitable "
            "SHL assessments for hiring. "
            "What role are you hiring for?"
        ),
        "recommendations": [],
        "end_of_conversation": False
    }


# -----------------------------
# CLARIFICATION RESPONSE
# -----------------------------

def clarification_response():

    return {
        "reply": (
            "Could you provide more details about "
            "the role, seniority level, and skills "
            "you are hiring for?"
        ),
        "recommendations": [],
        "end_of_conversation": False
    }


# -----------------------------
# REFUSAL RESPONSE
# -----------------------------

def refusal_response():

    return {
        "reply": (
            "I can only assist with SHL assessment "
            "recommendations and hiring-related queries."
        ),
        "recommendations": [],
        "end_of_conversation": False
    }


# -----------------------------
# COMPARISON RESPONSE
# -----------------------------

def comparison_response():

    return {
        "reply": (
            "Assessment comparison functionality "
            "will be implemented soon."
        ),
        "recommendations": [],
        "end_of_conversation": False
    }
    
    
# ----------------------------------------
# LOOKUP RESPONSE
# ----------------------------------------
# Handles direct assessment lookup queries.
# First tries exact title matching.
# Falls back to semantic FAISS retrieval
# if no exact match is found.
# ----------------------------------------
def lookup_response(conversation_context):

    query_lower = conversation_context.lower()

    exact_matches = []

    # -------------------------
    # EXACT TITLE MATCHING
    # -------------------------

    for item in metadata:

        title = item.get("title", "").lower()

        if title and title in query_lower:

            exact_matches.append(item)

    # -------------------------
    # FALLBACK TO FAISS
    # -------------------------

    if len(exact_matches) == 0:

        exact_matches = retrieve_assessments(
            conversation_context,
            top_k=3
        )

    recommendations = []

    for result in exact_matches[:10]:

        recommendation = {
            "name": result.get("title", ""),
            "url": result.get("url", ""),
            "pdf_url": result.get("pdf_url", ""),
            "test_type": "Unknown"
        }

        recommendations.append(recommendation)

    return {
        "reply": (
            "Here are the requested assessment links."
        ),
        "recommendations": recommendations,
        "end_of_conversation": True
    }

# -----------------------------
# RECOMMENDATION RESPONSE
# -----------------------------

def recommendation_response(conversation_context):

    retrieved_results = retrieve_assessments(
    conversation_context)

    llm_reply = generate_response(
        conversation_context)

    recommendations = []

    for result in retrieved_results[:10]:

        recommendation = {
    "name": result.get("title", ""),
    "url": result.get("url", ""),
    "pdf_url": result.get("pdf_url", ""),
    "test_type": "Unknown"
}

        recommendations.append(recommendation)

    return {
        "reply": llm_reply,
        "recommendations": recommendations,
        "end_of_conversation": True
    }


# -----------------------------
# MAIN CONVERSATION CONTROLLER
# -----------------------------
def process_query(messages):

    latest_query = messages[-1].content

    user_messages = []

    for msg in messages:

        if msg.role == "user":

            user_messages.append(msg.content)

    conversation_context = " ".join(user_messages)

    intent = classify_query(latest_query)

    print(f"Detected Intent: {intent}")

    if intent == "greeting":

        return greeting_response()

    elif intent == "vague":

        return clarification_response()

    elif intent == "off-topic":

        return refusal_response()

    elif intent == "comparison":

        return comparison_response()
    
    elif intent == "lookup":
        return lookup_response(
        conversation_context
    )
        
    elif intent == "recommendation":

        return recommendation_response(
            conversation_context
        )


    else:

        return {
            "reply": (
                "I could not understand your request clearly. "
                "Please provide more hiring-related details."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }