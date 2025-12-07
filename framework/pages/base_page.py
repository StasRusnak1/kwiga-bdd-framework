from framework.web.waits import wait_visible, wait_all

class BasePage:
    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def open(self, path: str = "/"):
        if not path.startswith("/"):
            path = "/" + path
        self.driver.get(self.base_url + path)

    def find_visible(self, locator):
        return wait_visible(self.driver, locator)

    def find_all_visible(self, locator):
        return wait_all(self.driver, locator)
