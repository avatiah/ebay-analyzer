import csv
import datetime
import requests
from bs4 import BeautifulSoup

def load_keywords():
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
        if not keywords:
            # если файл пустой — добавляем тестовое слово
            keywords = ["israel"]
            with open("keywords.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(keywords))
        return keywords
    except FileNotFoundError:
        # если файла нет — создаём с тестовым словом
        keywords = ["israel"]
        with open("keywords.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(keywords))
        return keywords

def scrape(keyword):
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select(".s-item")
    results = []
    for item in items[:5]:  # ограничим до 5 для теста
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
    keywords = load_keywords()
    all_rows = []
    for kw in keywords:
        results = scrape(kw)
        if results:
            all_rows.extend(results)
        else:
            # если ничего не найдено — пишем строку с ошибкой
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
    save_to_csv(all_rows)

if __name__ == "__main__":
    main()
