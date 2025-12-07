from dataclasses import dataclass, field
from typing import Optional
from .config import Config
from framework.web.driver_factory import create_driver

@dataclass
class Context:
    config: Config = field(default_factory=Config)
    driver: Optional[object] = None

    def init_driver(self):
        if self.driver is None:
            self.driver = create_driver(
                browser=self.config.browser,
                headless=self.config.headless,
                implicit_wait=self.config.implicit_wait,
            )

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
