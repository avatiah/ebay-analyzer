import csv, datetime, requests, os
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
    os.makedirs("data", exist_ok=True)
    header = ["timestamp","source","keyword","title","url","price","currency","watchers","avg_price","trend","sold","error"]
    with open("data/raw_data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if f.tell() == 0:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    keywords = load_keywords()
    if not keywords:
        print("Нет ключевых слов")
        return
    all_rows = []
    for kw in keywords:
        results = scrape(kw)
        if results:
            all_rows.extend(results)
        else:
            all_rows.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "ebay",
                "keyword": kw,
                "title": "",
                "url": "",
                "price": "",
                "currency": "",
                "watchers": "",
                "avg_price": "",
                "trend": "",
                "sold": "",
                "error": "no results"
            })
    if all_rows:
        save_to_csv(all_rows)

if __name__ == "__main__":
    main()
