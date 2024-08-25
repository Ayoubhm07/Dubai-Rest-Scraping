from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementClickInterceptedException
import time
import csv
import traceback


def get_element_safe(driver, locator, retries=3, delay=10):
    element = None
    while retries > 0:
        try:
            element = WebDriverWait(driver, delay).until(EC.presence_of_element_located(locator))
            return element
        except TimeoutException:
            retries -= 1
            print("Retrying to locate element: ", locator)
    return element


def refetch_elements(driver, xpath):
    return WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))


def safe_click(driver, locator):
    attempts = 0
    while attempts < 3:
        try:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator))
            element.click()
            return
        except ElementClickInterceptedException:
            attempts += 1
            print("Element intercepted, retrying click.")
        except TimeoutException:
            print("Click timeout reached, attempting JavaScript click.")
            driver.execute_script("arguments[0].click();",
                                  WebDriverWait(driver, 10).until(EC.element_to_be_clickable(locator)))


def wait_for_load(driver, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete")
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))
    except TimeoutException:
        print("Page load timed out but continuing with script execution.")


try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://dubailand.gov.ae/en/open-data/real-estate-data#/")

    rent_tab_locator = (By.ID, "rent-tab")
    safe_click(driver, rent_tab_locator)

    from_date = get_element_safe(driver, (By.ID, "rent_pFromDate"), 3, 10)
    from_date.clear()
    from_date.send_keys("01/07/2024")

    to_date = get_element_safe(driver, (By.ID, "rent_pToDate"), 3, 10)
    to_date.clear()
    to_date.send_keys("28/07/2024")
    to_date.send_keys(Keys.RETURN)  # Triggers the filter application
    to_date.send_keys(Keys.RETURN)  # Triggers the filter application
    time.sleep(10)

    wait_for_load(driver)

    select_element = Select(get_element_safe(driver, (By.NAME, "rentGrid_length")))
    select_element.select_by_value('100')

    desired_page = 5
    current_page = 1
    while current_page < desired_page:
        next_page_button = get_element_safe(driver, (By.CSS_SELECTOR, "button.page-link.next"), 3, 5)
        if next_page_button and next_page_button.get_attribute("aria-disabled") != "true":
            safe_click(driver, (By.CSS_SELECTOR, "button.page-link.next"))
            current_page += 1
            print(f"Moved to page {current_page}")
            wait_for_load(driver)
        else:
            print("Reached the end of pages or the specified page does not exist.")
            break

    with open('../rents_month2.csv', 'w', newline='') as file:
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
            safe_click(driver, next_button)

except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()

finally:
    driver.quit()
