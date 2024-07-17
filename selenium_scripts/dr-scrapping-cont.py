import traceback
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager


def get_element_safe(driver, locator, retries=3, delay=1):
    for _ in range(retries):
        try:
            element = driver.find_element(*locator)
            if element:
                return element
        except StaleElementReferenceException:
            time.sleep(delay)
    return None


def refetch_elements(driver, xpath):
    time.sleep(1)
    return driver.find_elements(By.XPATH, xpath)


def safe_click(element):
    attempts = 0
    while attempts < 3:
        try:
            element.click()
            return
        except ElementClickInterceptedException:
            ActionChains(driver).move_to_element(element).click(element).perform()
            attempts += 1
    # If normal clicks fail, use JavaScript to click
    driver.execute_script("arguments[0].click();", element)


try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://dubailand.gov.ae/en/open-data/real-estate-data#/")

    wait = WebDriverWait(driver, 60)

    # Set filters
    from_date = get_element_safe(driver, (By.ID, "transaction_pFromDate"))
    from_date.clear()
    from_date.send_keys("01/01/2024")

    transaction_type = get_element_safe(driver, (By.ID, "transaction_pTrxType"))
    transaction_type.click()
    sales_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//select[@id='transaction_pTrxType']/option[@value='1']")))
    sales_option.click()

    area_dropdown = get_element_safe(driver, (By.ID, "transaction_pAreaId_chosen"))
    area_dropdown.click()
    input_field = get_element_safe(driver, (By.XPATH, "//div[@id='transaction_pAreaId_chosen']//input"))
    input_field.send_keys('All')
    dubai_marina_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//ul[@class='chosen-results']/li[normalize-space()='All']")))
    dubai_marina_option.click()

    search_button = get_element_safe(driver, (By.XPATH, "//button[contains(text(), 'Search')]"))
    safe_click(search_button)

    wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))

    # Set rows to 100 per page
    select_element = wait.until(EC.visibility_of_element_located((By.NAME, "transactionGrid_length")))
    safe_click(select_element)
    option_100 = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//select[@name='transactionGrid_length']/option[@value='100']")))
    option_100.click()

    # Navigate progressively to page 209
    desired_page = 197
    current_page = 1
    while current_page < desired_page:
        next_page_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-link.next")))
        if "disabled" in next_page_link.get_attribute("class"):
            print("Reached the last available page before page 209.")
            break
        safe_click(next_page_link)
        current_page += 1
        print(f"Navigated to page {current_page}")
        wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))

    with open('real_estate_data_part2.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        first_page = True

        while True:
            wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))

            if first_page:
                headers = [header.text for header in
                           refetch_elements(driver, "//table[@id='transactionGrid']/thead/tr/th")]
                writer.writerow(headers)
                first_page = False

            rows = refetch_elements(driver, "//table[@id='transactionGrid']/tbody/tr")
            for row in rows:
                cells = [cell.text for cell in row.find_elements(By.TAG_NAME, "td")]
                writer.writerow(cells)

            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-link.next")))
            safe_click(next_button)

            if "disabled" in next_button.get_attribute("class"):
                break

except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()
finally:
    driver.quit()
