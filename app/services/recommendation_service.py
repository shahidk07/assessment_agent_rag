from app.services.llm_service import (
    generate_response,
    client
)

from app.services.retrieval_service import (
    retrieve_assessments
)


# -----------------------------
# INTENT CLASSIFICATION
# -----------------------------

def classify_query(query):

    prompt = f"""
    You are an intent classification system.

    Classify the user query into ONLY ONE category.

    Categories:
    - greeting
    - vague
    - recommendation
    - comparison
    - off-topic

    Rules:

    greeting:
    greetings like hi, hello, hey, good morning

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
    {query}
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


# -----------------------------
# RECOMMENDATION RESPONSE
# -----------------------------

def recommendation_response(query):

    retrieved_results = retrieve_assessments(query)

    llm_reply = generate_response(query)

    recommendations = []

    for result in retrieved_results[:10]:

        recommendation = {
            "name": result.get("title", ""),
            "url": result.get("url", ""),
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

def process_query(query):

    intent = classify_query(query)

    print(f"Detected Intent: {intent}")

    # GREETING
    if intent == "greeting":

        return greeting_response()

    # VAGUE QUERY
    elif intent == "vague":

        return clarification_response()

    # OFF TOPIC
    elif intent == "off-topic":

        return refusal_response()

    # COMPARISON
    elif intent == "comparison":

        return comparison_response()

    # RECOMMENDATION
    elif intent == "recommendation":

        return recommendation_response(query)

    # FALLBACK
    else:

        return {
            "reply": (
                "I could not understand your request clearly. "
                "Please provide more hiring-related details."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }