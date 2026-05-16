from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"


# -----------------------------------
# LOAD EMBEDDING MODEL
# -----------------------------------

model = SentenceTransformer(
    MODEL_NAME
)


# -----------------------------------
# LOAD FAISS INDEX
# -----------------------------------

index = faiss.read_index(
    "app/data/faiss_index/shl_index.faiss"
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
# RETRIEVAL FUNCTION
# -----------------------------------

def retrieve_assessments(
    query,
    top_k=5,
    use_threshold=True
):

    # -----------------------------------
    # EMBEDDING SEARCH
    # -----------------------------------

    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    results = []

    # -----------------------------------
    # THRESHOLD FILTERING
    # -----------------------------------

    for score, idx in zip(
        distances[0],
        indices[0]
    ):

        # reject weak matches
        if use_threshold and score > 1.2:
            continue

        results.append(metadata[idx])

    # -----------------------------------
    # LIGHTWEIGHT RERANKING
    # -----------------------------------

    query_lower = query.lower()

    boosted_results = []

    for item in results:

        text = (
            item.get("title", "") +
            " " +
            item.get("description", "")
        ).lower()

        boost_score = 0

        # -----------------------------------
        # DEVELOPER ROLES
        # -----------------------------------

        if (
            "developer" in query_lower
            and
            "developer" in text
        ):

            boost_score += 3

        # -----------------------------------
        # MANAGER ROLES
        # -----------------------------------

        if (
            "manager" in query_lower
            and
            "manager" in text
        ):

            boost_score += 3

        # -----------------------------------
        # SALES ROLES
        # -----------------------------------

        if (
            "sales" in query_lower
            and
            "sales" in text
        ):

            boost_score += 3

        # -----------------------------------
        # ANALYST ROLES
        # -----------------------------------

        if (
            "analyst" in query_lower
            and
            "analyst" in text
        ):

            boost_score += 3

        # -----------------------------------
        # INTERN / GRADUATE ROLES
        # -----------------------------------

        if (
            "intern" in query_lower
            and
            (
                "graduate" in text
                or
                "intern" in text
                or
                "apprentice" in text
            )
        ):

            boost_score += 2

        # -----------------------------------
        # MACHINE LEARNING / DATA
        # -----------------------------------

        if (
            (
                "machine learning" in query_lower
                or
                "data" in query_lower
            )
            and
            (
                "data" in text
                or
                "analytics" in text
                or
                "technical" in text
            )
        ):

            boost_score += 2

        boosted_results.append(
            (
                boost_score,
                item
            )
        )

    # -----------------------------------
    # SORT BY BOOST SCORE
    # -----------------------------------

    boosted_results.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    # -----------------------------------
    # FINAL SORTED RESULTS
    # -----------------------------------

    final_results = []

    for _, item in boosted_results:

        final_results.append(item)

    return final_results[:top_k]