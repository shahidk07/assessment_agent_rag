from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import json
import time


BASE_URL = "https://www.shl.com/products/product-catalog/?start={}&type=2&type=2"


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)


assessments = []

visited_urls = set()


# adjust range if needed
for start in range(0, 500, 12):

    url = BASE_URL.format(start)

    print(f"\nScraping page: {url}")

    driver.get(url)

    time.sleep(5)


    rows = driver.find_elements(By.TAG_NAME, "tr")


    page_count = 0


    for row in rows:

        try:

            link = row.find_element(By.TAG_NAME, "a")

            title = link.text.strip()

            assessment_url = link.get_attribute("href")

            if (
                title
                and assessment_url
                and "/products/product-catalog/view/" in assessment_url
                and assessment_url not in visited_urls
            ):

                assessment = {
                    "title": title,
                    "url": assessment_url
                }

                assessments.append(assessment)

                visited_urls.add(assessment_url)

                page_count += 1

                print(f"Saved: {title}")

        except:
            pass


    # stop if no assessments found
    if page_count == 0:

        print("No more assessments found.")
        break


with open("app/data/assessments.json", "w") as f:

    json.dump(assessments, f, indent=4)


driver.quit()


print(f"\nTotal assessments scraped: {len(assessments)}")