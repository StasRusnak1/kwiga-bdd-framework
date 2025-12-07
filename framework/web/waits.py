from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_visible(driver, locator, timeout=10):
    by, value = locator
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))

def wait_all(driver, locator, timeout=10):
    by, value = locator
    return WebDriverWait(driver, timeout).until(EC.visibility_of_all_elements_located((by, value)))
