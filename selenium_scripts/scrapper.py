from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time


# Configuration du pilote de navigateur pour Edge
service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service)

try:
    # Accéder à l'URL
    driver.get('https://dxbinteract.com/dubai-house-prices')

    # Attendre et cliquer sur 'Sold by' si disponible
    sold_by = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@data-id='sold-by']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", sold_by)
    driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));", sold_by)

    # Sélectionner 'Individual (ReSale)'
    individual_resale = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//li[@data-value='N']"))
    )
    driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));", individual_resale)

    # Cliquer sur le bouton 'Search'
    search_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='search-choose-btns submit-btn']"))
    )
    driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));", search_button)

    time.sleep(5)  # Attendre que les résultats soient chargés

    # Cliquer sur le bouton 'Download'
    download_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@onclick]//*[name()='svg']"))
    )
    driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));", download_button)

    time.sleep(5)  # Attendre que le téléchargement soit complet

finally:
    driver.quit()
