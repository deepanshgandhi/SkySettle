import requests
import json
import re
from bs4 import BeautifulSoup

URL = "https://www.transportation.gov/resources/individuals/aviation-consumer-protection/airline-cancellation-delay-dashboard-html"

def fetch_page(url=URL):
    """
    Downloads the webpage content from the given URL.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_cards(html):
    """
    Parses the HTML content to extract policy information from the collapsible cards.    
    Returns a list of dictionaries, one per airline card.
    """
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.card.paragraph--type--collapsible-html-block")
    results = []
    
    pattern = re.compile(r"^(.*?)’s?\s+Commitments for Controllable (Cancellations|Delays)$", re.IGNORECASE)
    
    for card in cards:
        header = card.find("div", class_="card-header")
        if header:
            title_tag = header.find("strong", class_="lead")
            title_text = title_tag.get_text(strip=True) if title_tag else ""
            m = pattern.match(title_text)
            if m:
                airline = m.group(1).strip()
                policy_type = m.group(2).strip().lower()  # cancellations or delays
            else:
                airline = title_text
                policy_type = ""
        else:
            airline = ""
            policy_type = ""
        
        card_block = card.find("div", class_="card-block")
        commits = []
        does_not_commit = []
        if card_block:
            ul_tags = card_block.find_all("ul")
            if len(ul_tags) >= 1:
                commits = [li.get_text(strip=True) for li in ul_tags[0].find_all("li")]
            if len(ul_tags) >= 2:
                does_not_commit = [li.get_text(strip=True) for li in ul_tags[1].find_all("li")]
        
        entry = {
            "airline": airline,
            "policy_type": policy_type,
            "commits": commits,
            "does_not_commit": does_not_commit
        }
        results.append(entry)
    
    return results

def scrape_and_save():
    """
    Combines the fetching and parsing of the webpage then saves the structured data to airline_policies.json.
    """
    html = fetch_page()
    data = parse_cards(html)
    with open("data/airline_policies.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Scraping complete. Data saved to airline_policies.json")

if __name__ == "__main__":
    scrape_and_save()