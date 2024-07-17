import csv
import traceback
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime, timedelta
import time


def get_element_safe(driver, locator, retries=3, delay=1):
    """ Tente de récupérer un élément plusieurs fois si nécessaire. """
    for _ in range(retries):
        try:
            return driver.find_element(*locator)
        except StaleElementReferenceException:
            time.sleep(delay)
    return driver.find_element(*locator)  # Dernière tentative sans capture d'exception


def refetch_elements(driver, xpath):
    """ Rafraîchit les éléments après une mise à jour du DOM pour éviter les éléments obsolètes. """
    time.sleep(1)  # Attente pour s'assurer que le DOM est stable
    return driver.find_elements(By.XPATH, xpath)


# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['scrapping_details']
collection = db['transactions']

# Récupérer la dernière transaction enregistrée pour définir les dates
last_transaction = collection.find().sort('_id', -1).limit(1).next()
last_to_date = last_transaction['to_date']
from_date_value = datetime.strptime(last_to_date, "%d/%m/%Y")
to_date_value = from_date_value + timedelta(days=6)

try:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://dubailand.gov.ae/en/open-data/real-estate-data#/")

    wait = WebDriverWait(driver, 10)

    from_date = get_element_safe(driver, (By.ID, "transaction_pFromDate"))
    from_date.clear()
    from_date.send_keys(from_date_value.strftime("%d/%m/%Y"))

    to_date = get_element_safe(driver, (By.ID, "transaction_pToDate"))
    to_date.clear()
    to_date.send_keys(to_date_value.strftime("%d/%m/%Y"))

    # Enregistrer les nouvelles dates de scrapping dans MongoDB
    collection.insert_one(
        {"from_date": from_date_value.strftime("%d/%m/%Y"), "to_date": to_date_value.strftime("%d/%m/%Y")})

    transaction_type = get_element_safe(driver, (By.ID, "transaction_pTrxType"))
    transaction_type.click()
    sales_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//select[@id='transaction_pTrxType']/option[@value='1']")))
    sales_option.click()

    area_dropdown = get_element_safe(driver, (By.ID, "transaction_pAreaId_chosen"))
    area_dropdown.click()
    input_field = get_element_safe(driver, (By.XPATH, "//div[@id='transaction_pAreaId_chosen']//input"))
    input_field.send_keys('DUBAI MARINA')
    dubai_marina_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//ul[@class='chosen-results']/li[normalize-space()='DUBAI MARINA']")))
    dubai_marina_option.click()

    search_button = get_element_safe(driver, (By.XPATH, "//button[contains(text(), 'Search')]"))
    search_button.click()

    # Ensure loader is gone before proceeding
    wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.cs-loader")))

    # Adjust the number of items shown in the table using JavaScript if necessary
    select_element = wait.until(EC.visibility_of_element_located((By.NAME, "transactionGrid_length")))
    driver.execute_script("arguments[0].scrollIntoView(true);", select_element)
    driver.execute_script("arguments[0].click();", select_element)

    option_100 = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//select[@name='transactionGrid_length']/option[@value='100']")))
    option_100.click()

    # CSV file setup
    with open('real_estate_data.csv', 'w', newline='') as file:
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
                writer.writerow([cell.text for cell in row.find_elements(By.TAG_NAME, "td")])

            next_button = get_element_safe(driver, (By.CSS_SELECTOR, "a.page-link.next"))
            if next_button.get_attribute("aria-disabled") == "true":
                break
            next_button.click()

except Exception as e:
    print("An error occurred:", str(e))
    traceback.print_exc()
