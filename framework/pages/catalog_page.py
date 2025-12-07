from selenium.webdriver.common.by import By
from .base_page import BasePage

class CatalogPage(BasePage):
    # Бере всі лінки на піддомени *.kwiga.com – серед них будуть назви курсів
    COURSE_TITLES = (
        By.XPATH,
        "//a[contains(@href, '.kwiga.com')]"
    )

    def get_course_titles(self):
        elements = self.find_all_visible(self.COURSE_TITLES)
        titles = [el.text.strip() for el in elements if el.text.strip()]
        return titles

    def sort_by(self, mode: str):
        # Цю частину можна доопрацювати пізніше, якщо реально є селект сортування.
        # Поки залишимо як заглушку, щоб не падало.
        pass
