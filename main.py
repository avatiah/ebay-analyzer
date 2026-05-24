import csv
import datetime
import requests
from bs4 import BeautifulSoup

def load_keywords():
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def scrape(keyword):
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select(".s-item")
    results = []
    for item in items[:10]:
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        link = item.select_one(".s-item__link")
        if title and price and link:
            results.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "ebay",
                "keyword": keyword,
                "title": title.get_text(strip=True),
                "url": link["href"],
                "price": price.get_text(strip=True),
                "currency": "",
                "watchers": "",
                "avg_price": "",
                "trend": "",
                "sold": "",
                "error": ""
            })
    return results

def save_to_csv(rows):
    header = ["timestamp","source","keyword","title","url","price","currency","watchers","avg_price","trend","sold","error"]
    with open("data/raw_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if f.tell() == 0:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
