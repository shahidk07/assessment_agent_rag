from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import json
import time


URL = "https://www.shl.com/solutions/products/product-catalog/"


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)


driver.get(URL)


# wait for javascript rendering
time.sleep(5)


rows = driver.find_elements(By.TAG_NAME, "tr")


assessments = []


for row in rows:

    try:

        link = row.find_element(By.TAG_NAME, "a")

        title = link.text.strip()

        url = link.get_attribute("href")

        if title:

            assessments.append({
                "title": title,
                "url": url
            })

    except:
        pass


with open("app/data/assessments.json", "w") as f:
    json.dump(assessments, f, indent=4)


print(f"Saved {len(assessments)} assessments.")


driver.quit()