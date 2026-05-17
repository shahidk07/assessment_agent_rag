from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

from groq import Groq

from dotenv import load_dotenv
import os


# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()


# -----------------------------------
# CONFIGURE GROQ CLIENT
# -----------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------------
# LOAD EMBEDDING MODEL
# -----------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
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
# BUILD CONCISE CONTEXT
# -----------------------------------

def build_concise_context(results):

    concise_context = ""

    for item in results[:3]:

        concise_context += f"""
        Assessment Name: {item.get('title', '')}

        Description:
        {item.get('description', '')}

        Job Levels:
        {item.get('job_levels', '')}

        Duration:
        {item.get('assessment_length', '')} minutes

        -------------------------
        """

    return concise_context


# -----------------------------------
# GENERATE RECOMMENDATION RESPONSE
# -----------------------------------

def generate_response(
    query,
    retrieved_results
):

    concise_context = build_concise_context(
        retrieved_results
    )

    prompt = f"""
You are an SHL assessment recommendation assistant.

Your job:
- recommend suitable SHL assessments,
- explain WHY the assessments fit the role,
- sound natural and recruiter-friendly,
- avoid robotic responses,
- use line breaks between ideas,
- avoid dense paragraphs
- avoid simply listing assessment names,
- focus on hiring relevance and evaluation areas,
- keep responses concise,
- maximum 2 short paragraphs,
- never invent assessments,
- only use the retrieved assessments provided below.
- do not infer unsupported role fit from the assessment title alone.
- only claim an assessment is role-specific when the title or description
  explicitly mentions that role, skill, or job family.
- if the retrieved assessments are broad or indirect matches, say they are
  the closest SHL matches and avoid pretending they are tailored to the
  exact role.

IMPORTANT:
The recommendation cards shown separately already contain:
- titles
- durations
- links
- PDFs

So your response should focus on:
- reasoning,
- hiring context,
- evaluation usefulness,
- recruiter guidance.

User Query:
{query}

Retrieved Assessments:
{concise_context}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        temperature=0.2,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------------------
# GENERATE COMPARISON RESPONSE
# -----------------------------------

def generate_comparison_response(
    first,
    second
):

    prompt = f"""
You are an SHL assessment comparison assistant.

Your job:
- compare the assessments clearly,
- explain differences in hiring usage,
- explain which situations each assessment fits best,
- avoid repeating metadata verbatim,
- sound conversational and recruiter-friendly,
- use headings and bullets,
- keep responses concise,
- never invent assessments,
- only use the information provided.

IMPORTANT:
Comparison cards shown separately already contain:
- titles
- durations
- job levels
- links
- languages

So focus mainly on:
- hiring differences,
- evaluation depth,
- recruiter decision-making,
- practical usage context,
- relative strengths and ideal use cases.

Output format:
- start with a short summary sentence,
- then provide 2-3 bullet points for each assessment,
- include 1 bullet describing their main difference.

Assessment 1:
Title: {first.get('title', '')}

Description:
{first.get('description', '')}

Job Levels:
{first.get('job_levels', '')}

Languages:
{first.get('languages', '')}

Duration:
{first.get('assessment_length', '')}


Assessment 2:
Title: {second.get('title', '')}

Description:
{second.get('description', '')}

Job Levels:
{second.get('job_levels', '')}

Languages:
{second.get('languages', '')}

Duration:
{second.get('assessment_length', '')}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        temperature=0.5,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
