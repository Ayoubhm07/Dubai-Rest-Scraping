from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import traceback


def get_element_safe(driver, locator, retries=3, delay=1):
    for _ in range(retries):
        try:
            return driver.find_element(*locator)
        except StaleElementReferenceException:
            time.sleep(delay)
    return None


def refetch_elements(driver, xpath):
    time.sleep(1)
    return driver.find_elements(By.XPATH, xpath)


def safe_click(driver, locator):
    element = wait_for_clickable(driver, locator)
    attempts = 0
    while attempts < 3:
        try:
            element.click()
            return
        except ElementClickInterceptedException:
            time.sleep(1)
            ActionChains(driver).move_to_element(element).click().perform()
            attempts += 1
        except TimeoutException:
            print("Click timeout reached.")
    driver.execute_script("arguments[0].click();", element)


def wait_for_clickable(driver, locator, timeout=60):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def wait_for_load(driver, timeout=60):
    """Wait for the loader to disappear and page to load completely."""
    WebDriverWait(driver, timeout).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    WebDriverWait(driver, timeout).until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))


try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://dubailand.gov.ae/en/open-data/real-estate-data#/")

    safe_click(driver, (By.ID, "rent-tab"))

    from_date = get_element_safe(driver, (By.ID, "rent_pFromDate"))
    from_date.clear()
    from_date.send_keys("01/05/2024")
    from_date.send_keys(Keys.RETURN)

    to_date = get_element_safe(driver, (By.ID, "rent_pToDate"))
    to_date.clear()
    to_date.send_keys("31/05/2024")
    to_date.send_keys(Keys.RETURN)

    wait_for_load(driver)

    select_element = Select(get_element_safe(driver, (By.NAME, "rentGrid_length")))
    select_element.select_by_value('100')

    # Desired start page number
    desired_page = 5
    current_page = 1
    while current_page < desired_page:
        next_page_link = wait_for_clickable(driver, (By.CSS_SELECTOR, "button.page-link.next"))
        safe_click(driver, next_page_link)
        current_page += 1
        wait_for_load(driver)

    with open('../continue.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        first_page = True
        while True:
            wait_for_load(driver)
            if first_page:
                headers = [header.text for header in refetch_elements(driver, "//table[@id='rentGrid']/thead/tr/th")]
                writer.writerow(headers)
                first_page = False

            rows = refetch_elements(driver, "//table[@id='rentGrid']/tbody/tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                writer.writerow([cell.text for cell in cells])

            next_button = get_element_safe(driver, (By.CSS_SELECTOR, "button.page-link.next"))
            if next_button.get_attribute("aria-disabled") == "true":
                break
            safe_click(driver, next_page_link)

except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()

finally:
    driver.quit()
