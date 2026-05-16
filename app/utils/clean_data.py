import json
import re


INPUT_FILE = "app/data/detailed_assessments.json"
OUTPUT_FILE = "app/data/cleaned_assessments.json"


with open(INPUT_FILE, "r") as f:
    assessments = json.load(f)


cleaned_assessments = []

visited_titles = set()


def clean_text(text):

    if not text:
        return ""

    # remove extra spaces/newlines
    text = re.sub(r"\s+", " ", text)

    return text.strip()


for assessment in assessments:

    title = clean_text(assessment.get("title", ""))

    description = clean_text(
        assessment.get("description", "")
    )

    url = clean_text(assessment.get("url", ""))

    job_levels = clean_text(
        assessment.get("job_levels", "")
    )

    languages = clean_text(
        assessment.get("languages", "")
    )

    assessment_length = clean_text(
        assessment.get("assessment_length", "")
    )

    pdf_url = clean_text(
        assessment.get("pdf_url", "")
    )


    # skip empty titles
    if not title:
        continue


    # remove duplicates
    if title in visited_titles:
        continue

    visited_titles.add(title)


    cleaned_assessment = {
        "title": title,
        "description": description,
        "url": url,
        "job_levels": job_levels,
        "languages": languages,
        "assessment_length": assessment_length,
        "pdf_url": pdf_url
    }


    cleaned_assessments.append(cleaned_assessment)


with open(OUTPUT_FILE, "w") as f:

    json.dump(cleaned_assessments, f, indent=4)


print(f"Cleaned {len(cleaned_assessments)} assessments.")