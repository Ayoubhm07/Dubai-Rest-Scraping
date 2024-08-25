from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementClickInterceptedException
import time
import csv
import traceback


def get_element_safe(driver, locator, retries=3, delay=3):
    for _ in range(retries):
        try:
            return driver.find_element(*locator)
        except StaleElementReferenceException:
            time.sleep(delay)
    return driver.find_element(*locator)


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
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))
    except TimeoutException:
        print("Le chargement a pris trop de temps, mais le script continue.")


try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://dubailand.gov.ae/en/open-data/real-estate-data#/")

    rent_tab_locator = (By.ID, "rent-tab")
    safe_click(driver, rent_tab_locator)

    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "rent_pFromDate")))
    from_date = get_element_safe(driver, (By.ID, "rent_pFromDate"))
    from_date.clear()
    from_date.send_keys("01/05/2024")
    from_date.send_keys(Keys.RETURN)

    time.sleep(1)

    # Attendre que les champs soient chargés
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "rent_pToDate")))
    to_date = get_element_safe(driver, (By.ID, "rent_pToDate"))
    to_date.clear()
    to_date.send_keys("31/05/2024")
    to_date.send_keys(Keys.RETURN)

    time.sleep(1)

    to_date.send_keys(Keys.RETURN)

    to_date.send_keys(Keys.RETURN)  

    wait_for_load(driver)

    select_element = Select(get_element_safe(driver, (By.NAME, "rentGrid_length")))
    select_element.select_by_value('100')

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
