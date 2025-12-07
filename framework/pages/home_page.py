from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage

class HomePage(BasePage):
    # Більш універсальний локатор для поля пошуку на каталозі Kwiga
    SEARCH_INPUT = (
        By.XPATH,
        "//input[contains(@placeholder, 'Щоб Ви хотіли вивчити сьогодні?')]"
    )
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".catalog-search__button")
    
    def open_home(self):
        # base_url вже містить /ua, тому просто відкриваємо корінь
        self.open("/")

    def search_course(self, query: str):
        search_input = self.find_visible(self.SEARCH_INPUT)
        search_input.clear()
        search_input.send_keys(query)
        # 2. Клікаємо по кнопці пошуку
        search_button = self.find_visible(self.SEARCH_BUTTON)
        search_button.click()
    
    def switch_language(self, lang: str):
        lang = lang.lower()
        # Для простоти: англійська = "/", українська = "/ua"
        if lang in ("uk", "ua", "ukrainian", "українська"):
            self.open("/ua")
        else:
            self.open("/")
