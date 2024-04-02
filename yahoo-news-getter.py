import re
import requests
from bs4 import BeautifulSoup
from time import sleep

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}

def get_article(card):
    """Extract article information from the raw html"""
    # Safely attempt to find and extract text from the h3 tag
    headline_tag = card.find('h3')
    headline = headline_tag.text if headline_tag else 'No Headline Available'

    source_tag = card.find("span", 'Fz(12px)')
    source = source_tag.text if source_tag else 'No Source Available'

    posted_tag = card.find('time')
    posted = posted_tag.text if posted_tag else 'No Time Available'

    description_tag = card.find('p')
    description = description_tag.text if description_tag else 'No Description Available'

    link_tag = card.find('a')
    link = link_tag['href'] if link_tag else 'No Link Available'

    if not link.startswith('http'):
        link = f"https://finance.yahoo.com{link}"

    article = (headline, source, posted, description, link)
    return article


def get_the_news(search):
    template = 'https://news.search.yahoo.com/search?p={}'
    url = template.format(search)
    articles = []
    links = set()
    
    while True:
        response = requests.get(url, headers=headers)
        print(response)  # For debugging purposes
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', 'NewsArticle')
            
            # If no cards are found, possibly an indication we're being blocked or wrong page structure
            if not cards:
                print("No articles found on the page, trying again in 5 seconds...")
                sleep(5)
                continue  # This continues the loop, retrying the same URL
            
            for card in cards:
                article = get_article(card)
                link = article[-1]
                if link not in links:
                    links.add(link)
                    articles.append(article)
                    
            try:
                url = soup.find('a', 'next').get('href')
                sleep(1)  # Respectful delay between requests
            except AttributeError:
                print("No more pages to fetch.")
                break  # Break the loop if there's no 'next' page
        else:
            print(f"Failed to fetch page: Status code {response.status_code}")
            break  # Exit loop on bad status code
            
    return articles

# Example usage
stock_ticker = 'AAPL'
news_articles = get_the_news(stock_ticker)
if news_articles:
    for article in news_articles:
        print(article)
else:
    print("No news articles found.")
