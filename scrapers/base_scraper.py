from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any

class BaseScraper(ABC):
    def __init__(self, start_url: str):
        self.start_url = start_url

    @abstractmethod
    def get_posts(self) -> Iterator[Dict[str, Any]]:
        """
        Yields post data.
        Each yielded item should be a dictionary with keys:
        - title: str
        - content: str (HTML)
        - date: str (optional)
        - url: str
        """
        pass
