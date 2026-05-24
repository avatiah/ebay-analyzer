import time
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from models import ProductRecord
from .base import BaseSource

class WatchCountSource(BaseSource):
    name = "watchcount"
    BASE_URL = "https://www.watchcount.com/completed.php"

    def fetch(self, keyword: str) -> List[ProductRecord]:
        params = {
            "s": keyword,
            "watched": 1,
            "ec1": "US",
        }

        resp = requests.get(self.BASE_URL, params=params, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        rows = soup.select("table tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            title_tag = cols[0].find("a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            url = title_tag.get("href") or ""

            price_text = cols[1].get_text(strip=True)
            watchers_text = cols[2].get_text(strip=True)

            price = None
            currency = None

            if price_text:
                currency = price_text[0]
                try:
                    price = float(price_text[1:].replace(",", ""))
                except:
                    price = None

            watchers = None
            if watchers_text:
                digits = "".join(ch for ch in watchers_text if ch.isdigit())
                watchers = int(digits) if digits else None

            results.append(ProductRecord(
                source=self.name,
                keyword=keyword,
                title=title,
                url=url,
                price=price,
                currency=currency,
                watchers=watchers,
                sold=None,
            ))

        time.sleep(2)
        return results
