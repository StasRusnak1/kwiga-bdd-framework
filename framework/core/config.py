from dataclasses import dataclass

@dataclass
class Config:
    base_url: str = "https://kwiga.com/"
    browser: str = "chrome"
    headless: bool = True
    implicit_wait: int = 5
    explicit_wait: int = 10
