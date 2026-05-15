from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import json
import time


# load basic assessment list
with open("app/data/assessments.json", "r") as f:
    assessments = json.load(f)


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)


detailed_assessments = []


for assessment in assessments:

    url = assessment["url"]

    print(f"Scraping: {url}")

    driver.get(url)

    time.sleep(3)

    try:

        # TITLE
        title = driver.find_element(By.TAG_NAME, "h1").text


        # DESCRIPTION
        description = ""

        try:

            description_sections = driver.find_elements(
                By.CLASS_NAME,
                "product-catalogue-training-calendar__row"
            )

            for section in description_sections:

                if "Description" in section.text:

                    description = section.find_element(
                        By.TAG_NAME,
                        "p"
                    ).text

                    break

        except:
            pass

        # PAGE TEXT
        page_text = driver.find_element(By.TAG_NAME, "body").text


        # JOB LEVELS
        job_levels = ""

        if "Job levels" in page_text:

            try:
                job_levels = page_text.split("Job levels")[1].split("Languages")[0].strip()
            except:
                pass


        # LANGUAGES
        languages = ""

        if "Languages" in page_text:

            try:
                languages = page_text.split("Languages")[1].split("Assessment length")[0].strip()
            except:
                pass


        # ASSESSMENT LENGTH
        assessment_length = ""

        if "Approximate Completion Time" in page_text:

            try:
                assessment_length = page_text.split(
                    "Approximate Completion Time in minutes ="
                )[1].split("\n")[0].strip()
            except:
                pass


        # PDF URL
        pdf_url = ""

        links = driver.find_elements(By.TAG_NAME, "a")

        for link in links:

            href = link.get_attribute("href")

            if href and href.endswith(".pdf"):

                pdf_url = href
                break


        detailed_assessment = {
            "title": title,
            "url": url,
            "description": description,
            "job_levels": job_levels,
            "languages": languages,
            "assessment_length": assessment_length,
            "pdf_url": pdf_url
        }


        detailed_assessments.append(detailed_assessment)

        print(f"Saved: {title}")


    except Exception as e:

        print(f"Error scraping {url}")
        print(e)


with open("app/data/detailed_assessments.json", "w") as f:

    json.dump(detailed_assessments, f, indent=4)


driver.quit()


print("Detailed scraping completed.")