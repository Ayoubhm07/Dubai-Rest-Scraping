import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementClickInterceptedException
import time
import csv


def get_element_safe(driver, locator, retries=3, delay=1):
    for _ in range(retries):
        try:
            return driver.find_element(*locator)
        except StaleElementReferenceException:
            time.sleep(delay)
    return driver.find_element(*locator)


def refetch_elements(driver, xpath):
    time.sleep(1)
    return driver.find_elements(By.XPATH, xpath)


def safe_click(element, driver):
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


def wait_for_load(driver, timeout=60):
    """Wait for the loader to disappear and page to load completely."""
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

    from_date = get_element_safe(driver, (By.ID, "transaction_pFromDate"))
    from_date.clear()
    from_date.send_keys("01/01/2024")

    transaction_type = get_element_safe(driver, (By.ID, "transaction_pTrxType"))
    transaction_type.click()
    sales_option = get_element_safe(driver, (By.XPATH, "//select[@id='transaction_pTrxType']/option[@value='1']"))
    safe_click(sales_option, driver)

    area_dropdown = get_element_safe(driver, (By.ID, "transaction_pAreaId_chosen"))
    area_dropdown.click()
    input_field = get_element_safe(driver, (By.XPATH, "//div[@id='transaction_pAreaId_chosen']//input"))
    input_field.send_keys('All')
    dubai_marina_option = get_element_safe(driver,
                                           (By.XPATH, "//ul[@class='chosen-results']/li[normalize-space()='All']"))
    safe_click(dubai_marina_option, driver)

    search_button = get_element_safe(driver, (By.XPATH, "//button[contains(text(), 'Search')]"))
    safe_click(search_button, driver)

    wait_for_load(driver)

    select_element = get_element_safe(driver, (By.NAME, "transactionGrid_length"))
    safe_click(select_element, driver)

    option_100 = get_element_safe(driver, (By.XPATH, "//select[@name='transactionGrid_length']/option[@value='100']"))
    safe_click(option_100, driver)

    with open('../real_estate_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        first_page = True
        while True:
            wait_for_load(driver)
            if first_page:
                headers = [header.text for header in
                           refetch_elements(driver, "//table[@id='transactionGrid']/thead/tr/th")]
                writer.writerow(headers)
                first_page = False

            rows = refetch_elements(driver, "//table[@id='transactionGrid']/tbody/tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")  # Optimized to avoid refetching if not necessary
                writer.writerow([cell.text for cell in cells])

            next_button = get_element_safe(driver, (By.CSS_SELECTOR, "a.page-link.next"))
            if "disabled" in next_button.get_attribute("class"):
                break
            safe_click(next_button, driver)

except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()
finally:
    driver.quit()
