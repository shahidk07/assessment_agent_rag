from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
import pickle


MODEL_NAME = "all-MiniLM-L6-v2"


# load cleaned data
with open("app/data/detailed_assessments.json", "r") as f:
    assessments = json.load(f)


model = SentenceTransformer(MODEL_NAME)


documents = []


for assessment in assessments:

    text = f"""
    Title: {assessment.get("title", "")}
    Description: {assessment.get("description", "")}
    Job Levels: {assessment.get("job_levels", "")}
    Languages: {assessment.get("languages", "")}
    """

    documents.append(text)


print("Creating embeddings...")


embeddings = model.encode(documents)


embedding_dimension = embeddings.shape[1]


index = faiss.IndexFlatL2(embedding_dimension)


index.add(np.array(embeddings))


# save faiss index
faiss.write_index(
    index,
    "app/data/faiss_index/shl_index.faiss"
)


# save metadata
with open(
    "app/data/faiss_index/metadata.pkl",
    "wb"
) as f:

    pickle.dump(assessments, f)


print("Embeddings + FAISS index created successfully.")