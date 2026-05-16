from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"


# load embedding model
model = SentenceTransformer(MODEL_NAME)


# load faiss index
index = faiss.read_index(
    "app/data/faiss_index/shl_index.faiss"
)


# load metadata
with open(
    "app/data/faiss_index/metadata.pkl",
    "rb"
) as f:

    metadata = pickle.load(f)


def retrieve_assessments(query, top_k=5):

    # convert query into embedding
    query_embedding = model.encode([query])

    # search faiss
    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    results = []

    for idx in indices[0]:

        results.append(metadata[idx])

    return results


# # TEST QUERY
# query = "Leadership assessments for managers"


# results = retrieve_assessments(query)


# print("\nTop Matching Assessments:\n")


# for i, result in enumerate(results, start=1):

#     print(f"{i}. {result['title']}")

#     print(f"Job Levels: {result['job_levels']}")

#     print(f"Duration: {result['assessment_length']} mins")

#     print(f"URL: {result['url']}")

#     print("-" * 50)