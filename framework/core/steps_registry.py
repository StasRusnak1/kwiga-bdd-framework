import re
from typing import Callable, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from framework.core.assertions import assert_contains
from framework.pages.home_page import HomePage
from framework.pages.catalog_page import CatalogPage


class StepsRegistry:
    def __init__(self, ctx):
        self.ctx = ctx
        self._steps: List[Tuple[re.Pattern, Callable]] = []
        self._register_default_steps()

    def _register(self, pattern: str, func: Callable):
        self._steps.append((re.compile(pattern), func))

    def _register_default_steps(self):
        # Базові кроки налаштування
        self._register(r'^app baseUrl "(.+)"$', self.step_set_base_url)
        self._register(r'^browser "(\w+)" headless (true|false)$', self.step_set_browser)

        # Навігація на головну
        self._register(r'^I open "home"$', self.step_open_home)

        # Пошук курсу (unlock.kwiga.com)
        self._register(r'^I search course "(.+)"$', self.step_search_course)
        self._register(r'^I expect results contain title "(.+)"$', self.step_expect_result_title)

        # Перемикання мови (kwiga.com ↔ kwiga.com/ua)
        self._register(r'^I switch language to "(.+)"$', self.step_switch_language)
        self._register(r'^I expect page language is "(.+)"$', self.step_expect_page_language)

        # Додаткові кроки для головного сайту kwiga.com
        self._register(r'^I click header menu "(.+)"$', self.step_click_header_menu)
        self._register(r'^I click footer link "(.+)"$', self.step_click_footer_link)
        self._register(r'^I click button "(.+)"$', self.step_click_button)
        self._register(r'^I click css "(.+)"$', self.step_click_css)
        self._register(r'^I click header dropdown "(.+)"$', self.step_click_header_dropdown)
        self._register(r'^I expect page contains text "(.+)"$', self.step_expect_page_contains_text)
        self._register(r'^I expect current url contains "(.+)"$', self.step_expect_current_url_contains)

        # Крок для роботи з новою вкладкою (Book a demo)
        self._register(r'^I switch to new tab$', self.step_switch_to_new_tab)

    # --------------------
    # Базові кроки
    # --------------------

    def step_set_base_url(self, m):
        """Given app baseUrl "<url>"."""
        self.ctx.config.base_url = m.group(1)

    def step_set_browser(self, m):
        """And browser "<name>" headless <true|false>."""
        browser = m.group(1)
        headless = m.group(2).lower() == "true"
        self.ctx.config.browser = browser
        self.ctx.config.headless = headless

    def step_open_home(self, m):
        """When I open "home"."""
        self.ctx.init_driver()
        hp = HomePage(self.ctx.driver, self.ctx.config.base_url)
        hp.open_home()

    # --------------------
    # Пошук курсів (unlock.kwiga.com)
    # --------------------

    def step_search_course(self, m):
        """And I search course "<query>"."""
        query = m.group(1)
        self.ctx.init_driver()
        hp = HomePage(self.ctx.driver, self.ctx.config.base_url)
        hp.search_course(query)

    def step_expect_result_title(self, m):
        """Then I expect results contain title "<title>"."""
        expected = m.group(1)
        self.ctx.init_driver()
        cp = CatalogPage(self.ctx.driver, self.ctx.config.base_url)
        titles = cp.get_course_titles()
        assert_contains(
            titles,
            expected,
            f'Expected "{expected}" in results, got: {titles}',
        )

    # --------------------
    # Перемикання мови (kwiga.com)
    # --------------------

    def step_switch_language(self, m):
        """And I switch language to "<lang>"."""
        lang = m.group(1).lower()
        self.ctx.init_driver()
        hp = HomePage(self.ctx.driver, self.ctx.config.base_url)
        hp.switch_language(lang)

    def step_expect_page_language(self, m):
        """Then I expect page language is "<lang>"."""
        lang = m.group(1).lower()
        self.ctx.init_driver()
        page_source = self.ctx.driver.page_source

        if lang in ("uk", "ua", "ukrainian", "українська"):
            expected_snippet = "Усі інструменти для успішного бізнесу"
        else:
            expected_snippet = "All tools for a successful business"

        assert_contains(
            page_source,
            expected_snippet,
            f'Expected language "{lang}" snippet "{expected_snippet}" not found on page',
        )

    # --------------------
    # Додаткові кроки для головної сторінки kwiga.com
    # --------------------

    def step_click_header_menu(self, m):
        """
        And I click header menu "<text>".
        Шукай лінк у хедері за видимим текстом, напр. "LMS", "Sign in".
        """
        text = m.group(1)
        self.ctx.init_driver()
        driver = self.ctx.driver

        link = driver.find_element(By.LINK_TEXT, text)
        link.click()

    def step_click_footer_link(self, m):
        """
        And I click footer link "<text>".
        Використовує LINK_TEXT, напр. "List of courses", "Book a demo".
        """
        text = m.group(1)
        self.ctx.init_driver()
        driver = self.ctx.driver

        link = driver.find_element(By.LINK_TEXT, text)
        link.click()

    def step_click_button(self, m):
        """
        And I click button "<text>".
        Шукаємо будь-яку кнопку/лінк з вказаним текстом (наприклад, "Start now").
        """
        label = m.group(1)
        self.ctx.init_driver()
        driver = self.ctx.driver

        xpath = (
            f"//a[normalize-space(.)='{label}' or contains(normalize-space(.), '{label}')]"
            f" | //button[normalize-space(.)='{label}' or contains(normalize-space(.), '{label}')]"
        )
        element = driver.find_element(By.XPATH, xpath)
        element.click()

    def step_click_css(self, m):
        """
        And I click css "<selector>".
        Загальний крок для кліку по CSS-селектору.
        """
        selector = m.group(1)
        self.ctx.init_driver()
        driver = self.ctx.driver

        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()

    def step_click_header_dropdown(self, m):
        """
        And I click header dropdown "<text>".
        Шукає елемент .header__menu_item_dropdown, який містить вказаний текст (наприклад, "Useful info").
        """
        label = m.group(1).strip().lower()
        self.ctx.init_driver()
        driver = self.ctx.driver

        items = driver.find_elements(By.CSS_SELECTOR, ".header__menu_item_dropdown")
        for item in items:
            text = item.text.strip().lower()
            if label in text:
                item.click()
                return

        visible_texts = [i.text.strip() for i in items]
        raise AssertionError(
            f'Header dropdown with text "{m.group(1)}" not found. '
            f'Available dropdowns: {visible_texts}'
        )

    def step_expect_page_contains_text(self, m):
        """
        Then I expect page contains text "<snippet>".
        Чекаємо до 10 секунд, поки текст з'явиться на сторінці.
        """
        snippet = m.group(1)
        self.ctx.init_driver()
        driver = self.ctx.driver

        WebDriverWait(driver, 10).until(
            lambda d: snippet in d.page_source
        )

        page_source = driver.page_source
        assert_contains(
            page_source,
            snippet,
            f'Expected to find text "{snippet}" on page, but it was not found.',
        )

    def step_expect_current_url_contains(self, m):
        """
        Then I expect current url contains "<part>".
        """
        part = m.group(1)
        self.ctx.init_driver()
        current_url = self.ctx.driver.current_url
        assert_contains(
            current_url,
            part,
            f'Expected current URL to contain "{part}", got: {current_url}',
        )

    # --------------------
    # Крок для вкладки
    # --------------------

    def step_switch_to_new_tab(self, m):
        """
        And I switch to new tab.
        Перемикаємось на останню вкладку (наприклад, Calendly).
        """
        self.ctx.init_driver()
        driver = self.ctx.driver

        handles = driver.window_handles
        if len(handles) > 1:
            driver.switch_to.window(handles[-1])

    # --------------------
    # Виконання кроку
    # --------------------

    def execute_step(self, step_text: str):
        for pattern, func in self._steps:
            m = pattern.match(step_text)
            if m:
                return func(m)
        raise ValueError(f"No step definition matches: {step_text}")
