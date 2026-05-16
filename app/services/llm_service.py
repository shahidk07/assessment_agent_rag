from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

from groq import Groq

from dotenv import load_dotenv
import os


# LOAD ENV VARIABLES
load_dotenv()

# CONFIGURE GROQ CLIENT
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# LOAD EMBEDDING MODEL
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# LOAD FAISS INDEX
index = faiss.read_index(
    "app/data/faiss_index/shl_index.faiss"
)


# LOAD METADATA
with open(
    "app/data/faiss_index/metadata.pkl",
    "rb"
) as f:

    metadata = pickle.load(f)


def retrieve_assessments(query, top_k=5):

    query_embedding = embedding_model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    results = []

    for idx in indices[0]:

        results.append(metadata[idx])

    return results


def build_context(results):

    context = ""

    for result in results:

        context += f"""
        Title: {result.get('title', '')}

        Description:
        {result.get('description', '')}

        Job Levels:
        {result.get('job_levels', '')}

        Assessment Length:
        {result.get('assessment_length', '')} minutes

        URL:
        {result.get('url', '')}

        --------------------------------
        """

    return context


def generate_response(query):

    retrieved_results = retrieve_assessments(query)

    context = build_context(retrieved_results)

    prompt = f"""
    You are an AI assistant helping recruiters
    recommend SHL assessments.

    Recruiter Query:
    {query}

    Available Assessments:
    {context}

    Instructions:
    - Recommend the most relevant assessments
    - Explain WHY each assessment matches
    - Keep response professional and concise
    """


    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
    )

    return response.choices[0].message.content


# TEST
# query = input("Enter recruiter query: ")

# answer = generate_response(query)

# print("\nAI RESPONSE:\n")

# print(answer)