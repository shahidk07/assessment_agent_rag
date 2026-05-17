from app.services.llm_service import (
    generate_response,
    generate_comparison_response,
    client
)

import pickle
import re

from app.services.retrieval_service import (
    retrieve_assessments
)


# -----------------------------------
# LOAD METADATA
# -----------------------------------

with open(
    "app/data/faiss_index/metadata.pkl",
    "rb"
) as f:

    metadata = pickle.load(f)


# -----------------------------------
# INTENT CLASSIFICATION
# -----------------------------------

GENERIC_REQUEST_WORDS = {
    "a",
    "an",
    "and",
    "any",
    "assessment",
    "assessments",
    "candidate",
    "candidates",
    "employment",
    "evaluation",
    "evaluations",
    "find",
    "for",
    "get",
    "give",
    "help",
    "hire",
    "hiring",
    "i",
    "me",
    "need",
    "please",
    "pre",
    "recruit",
    "recruiting",
    "recruitment",
    "recommend",
    "screen",
    "screening",
    "shl",
    "some",
    "suggest",
    "test",
    "tests",
    "the",
    "to",
    "use",
    "want",
    "we",
    "with",
}

ASSESSMENT_REQUEST_WORDS = {
    "assessment",
    "assessments",
    "evaluation",
    "evaluations",
    "hire",
    "hiring",
    "recruit",
    "recruiting",
    "screen",
    "screening",
    "test",
    "tests",
}

OFF_TOPIC_WORDS = {
    "bootcamp",
    "bootcamps",
    "certificate",
    "certificates",
    "certification",
    "certifications",
    "course",
    "courses",
    "coursera",
    "degree",
    "degrees",
    "edx",
    "lesson",
    "lessons",
    "mooc",
    "moocs",
    "program",
    "programs",
    "training",
    "tutorial",
    "tutorials",
    "udemy",
}

HARD_OFF_TOPIC_WORDS = {
    "bootcamp",
    "bootcamps",
    "certificate",
    "certificates",
    "certification",
    "certifications",
    "course",
    "courses",
    "coursera",
    "degree",
    "degrees",
    "edx",
    "lesson",
    "lessons",
    "mooc",
    "moocs",
    "tutorial",
    "tutorials",
    "udemy",
    "youtube",
}

ASSESSMENT_PRODUCT_WORDS = {
    "assessment",
    "assessments",
    "evaluation",
    "evaluations",
    "screen",
    "screening",
    "shl",
    "test",
    "tests",
}


def tokenize_query(latest_query):

    return re.findall(
        r"[a-z0-9+#.]+",
        latest_query.lower()
    )


def is_off_topic_request(latest_query):

    tokens = tokenize_query(latest_query)

    if not tokens:
        return False

    has_off_topic_word = any(
        token in OFF_TOPIC_WORDS
        for token in tokens
    )

    has_hard_off_topic_word = any(
        token in HARD_OFF_TOPIC_WORDS
        for token in tokens
    )

    has_assessment_product_word = any(
        token in ASSESSMENT_PRODUCT_WORDS
        for token in tokens
    )

    return (
        has_hard_off_topic_word or
        (
            has_off_topic_word and
            not has_assessment_product_word
        )
    )


def is_vague_assessment_request(latest_query):

    tokens = tokenize_query(latest_query)

    if not tokens:
        return True

    has_assessment_request = any(
        token in ASSESSMENT_REQUEST_WORDS
        for token in tokens
    )

    if not has_assessment_request:
        return False

    context_tokens = [
        token
        for token in tokens
        if token not in GENERIC_REQUEST_WORDS
    ]

    return len(context_tokens) == 0


def classify_query(latest_query):

    query = latest_query.lower()

    # -----------------------------------
    # RULE-BASED SHORTCUTS
    # -----------------------------------

    recommendation_keywords = [
        "assessment",
        "assessments",
        "hire",
        "hiring",
        "developer",
        "engineer",
        "intern",
        "manager",
        "analyst",
        "machine learning",
        "java",
        "sales",
        "data",
        "role"
    ]

    comparison_keywords = [
        "compare",
        "comparison"
    ]

    greeting_keywords = [
        "hi",
        "hello",
        "hey",
        "hii"
    ]

    lookup_keywords = [
        "pdf",
        "link",
        "download",
        "open"
    ]

    # GREETING
    if query in greeting_keywords:
        return "greeting"

    # OFF-TOPIC
    # Non-SHL training/course requests should refuse before LLM fallback.
    if is_off_topic_request(latest_query):
        return "off-topic"

    # VAGUE ASSESSMENT REQUEST
    # Generic requests should ask for role/skill context before retrieval.
    if is_vague_assessment_request(latest_query):
        return "vague"

    # COMPARISON
    if any(word in query for word in comparison_keywords):
        return "comparison"

    # LOOKUP
    if any(word in query for word in lookup_keywords):
        return "lookup"

    # RECOMMENDATION
    if any(word in query for word in recommendation_keywords):
        return "recommendation"

    # -----------------------------------
    # LLM FALLBACK CLASSIFICATION
    # -----------------------------------

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

    intent = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .lower()
    )

    return intent


# -----------------------------------
# GREETING RESPONSE
# -----------------------------------

def greeting_response():

    return {
        "reply": (
            "Hello! I can help you discover "
            "SHL hiring assessments. "
            "What role are you hiring for?"
        ),
        "recommendations": [],
        "comparison": False,
        "comparison_data": [],
        "end_of_conversation": False
    }


# -----------------------------------
# CLARIFICATION RESPONSE
# -----------------------------------

def clarification_response():

    return {
        "reply": (
            "Could you share more details about "
            "the role, seniority level, or skills "
            "you are hiring for?"
        ),
        "recommendations": [],
        "comparison": False,
        "comparison_data": [],
        "end_of_conversation": False
    }


# -----------------------------------
# REFUSAL RESPONSE
# -----------------------------------

def refusal_response():

    return {
        "reply": (
            "I can only help with SHL assessment "
            "recommendations and hiring-related queries."
        ),
        "recommendations": [],
        "comparison": False,
        "comparison_data": [],
        "end_of_conversation": False
    }


# -----------------------------------
# COMPARISON RESPONSE
# -----------------------------------

def comparison_response(conversation_context):

    retrieved_results = retrieve_assessments(
        conversation_context,
        top_k=2
    )

    # Handle edge case: less than 2 assessments found
    if len(retrieved_results) < 2:

        return {
            "reply": (
                "I found fewer than 2 assessments to compare. "
                "Please specify assessment names or roles. "
                "For example: 'Compare OPQ and GSA' or 'Compare manager assessments.'"
            ),
            "recommendations": [],
            "comparison": False,
            "comparison_data": [],
            "error": "insufficient_results",
            "end_of_conversation": False
        }

    first = retrieved_results[0]
    second = retrieved_results[1]

    # Validate comparison data
    if not first or not second:
        return {
            "reply": "Unable to retrieve assessment data. Please try again.",
            "recommendations": [],
            "comparison": False,
            "comparison_data": [],
            "error": "data_validation_failed",
            "end_of_conversation": False
        }

    llm_reply = generate_comparison_response(
        first,
        second
    )

    return {
        "reply": llm_reply,
        "recommendations": [],
        "comparison": True,
        "comparison_data": [
            first,
            second
        ],
        "error": None,
        "end_of_conversation": True
    }


# -----------------------------------
# LOOKUP RESPONSE
# -----------------------------------

def lookup_response(conversation_context):

    query_lower = conversation_context.lower()

    exact_matches = []

    for item in metadata:

        title = item.get(
            "title",
            ""
        ).lower()

        if title and title in query_lower:

            exact_matches.append(item)

    if len(exact_matches) == 0:

        exact_matches = retrieve_assessments(
            conversation_context,
            top_k=3
        )

    recommendations = []

    for result in exact_matches[:3]:

        recommendations.append({
            "name": result.get("title", ""),
            "url": result.get("url", ""),
            "pdf_url": result.get("pdf_url", ""),
            "duration": result.get(
                "assessment_length",
                "N/A"
            ),
            "test_type": "A"
        })

    return {
        "reply": (
            "I found these matching assessments."
        ),
        "recommendations": recommendations,
        "comparison": False,
        "comparison_data": [],
        "end_of_conversation": True
    }


# -----------------------------------
# RECOMMENDATION RESPONSE
# -----------------------------------

def recommendation_response(
    conversation_context,
    use_threshold=True
):

    retrieved_results = retrieve_assessments(
        conversation_context,
        use_threshold=use_threshold
    )

    # -----------------------------------
    # NO RESULTS
    # -----------------------------------

    if len(retrieved_results) == 0:

        return {
            "reply": (
                "I could not find assessments "
                "specific to this domain. "
                "However, I can recommend broader "
                "personality, aptitude, and cognitive "
                "assessments that work across many roles. "
                "Would you like those recommendations?"
            ),
            "recommendations": [],
            "comparison": False,
            "comparison_data": [],
            "end_of_conversation": False
        }

    # -----------------------------------
    # LLM RESPONSE
    # -----------------------------------

    llm_reply = generate_response(
        conversation_context,
        retrieved_results
    )

    recommendations = []

    for result in retrieved_results[:3]:

        recommendations.append({

            "name": result.get(
                "title",
                ""
            ),

            "url": result.get(
                "url",
                ""
            ),

            "pdf_url": result.get(
                "pdf_url",
                ""
            ),

            "duration": result.get(
                "assessment_length",
                "N/A"
            ),

            "test_type": "A"
        })

    return {
        "reply": llm_reply,
        "recommendations": recommendations,
        "comparison": False,
        "comparison_data": [],
        "end_of_conversation": True
    }


# -----------------------------------
# MAIN CONTROLLER
# -----------------------------------

def process_query(messages):

    latest_query = messages[-1].content

    latest_query_lower = latest_query.lower()

    user_messages = []

    for msg in messages:

        if msg.role == "user":

            user_messages.append(
                msg.content
            )

    conversation_context = " ".join(
        user_messages
    )

    # -----------------------------------
    # PREVIOUS ASSISTANT MESSAGE
    # -----------------------------------

    previous_assistant = ""

    for msg in reversed(messages):

        if msg.role == "assistant":

            previous_assistant = (
                msg.content.lower()
            )

            break

    # -----------------------------------
    # FALLBACK FLOW
    # -----------------------------------

    fallback_active = (
        "broader personality" in previous_assistant
    )

    clarification_active = (
        "role, seniority level, or skills" in previous_assistant or
        "what role are you hiring for" in previous_assistant
    )

    if (
        fallback_active and
        latest_query_lower in [
            "yes",
            "yeah",
            "sure",
            "okay",
            "ok",
            "yup"
        ]
    ):

        return recommendation_response(
            "OPQ personality aptitude professional",
            use_threshold=False
        )

    if (
        fallback_active and
        latest_query_lower in [
            "no",
            "nah",
            "nope",
            "nahi"
        ]
    ):

        return {
            "reply": (
                "Alright. Let me know if you need help "
                "with any other SHL assessments."
            ),
            "recommendations": [],
            "comparison": False,
            "comparison_data": [],
            "end_of_conversation": True
        }

    # -----------------------------------
    # INTENT DETECTION
    # -----------------------------------

    intent_query = latest_query

    if clarification_active:
        intent_query = conversation_context

    intent = classify_query(
        intent_query
    )

    print(f"Detected Intent: {intent}")

    # -----------------------------------
    # ROUTING
    # -----------------------------------

    if intent == "greeting":

        return greeting_response()

    elif intent == "vague":

        return clarification_response()

    elif intent == "off-topic":

        return refusal_response()

    elif intent == "comparison":

        return comparison_response(
            conversation_context
        )

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
            "comparison": False,
            "comparison_data": [],
            "end_of_conversation": False
        }
