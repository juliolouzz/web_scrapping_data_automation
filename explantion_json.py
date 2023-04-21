import os
from bs4 import BeautifulSoup
import requests
import json

zillow_url = os.environ.get("ZILLOW_URL")

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Accept-Language": "en-US,en;q=0.5",
}

r = requests.get(zillow_url, headers=header)
zillow_results = r.text
soup = BeautifulSoup(zillow_results, "html.parser")

data = json.loads(
    soup.select_one("script[data-zrr-shared-data-key]")
    .contents[0]
    # .text
    .strip("!<>-")
)

# get house links
house_links = [
    result["detailUrl"]
    for result in data["cat1"]["searchResults"]["listResults"]
]

# amend house_links to have all proper URLS
house_links = [
    link.replace(link, "https://www.zillow.com" + link)
    if not link.startswith("http")
    else link
    for link in house_links
]

# Get address
house_address = [
    result["address"]
    for result in data["cat1"]["searchResults"]["listResults"]
]

# Get price
house_rent = [
    int(result["units"][0]["price"].strip("$").replace(",", "").strip("+"))
    if "units" in result
    else result["unformattedPrice"]
    for result in data["cat1"]["searchResults"]["listResults"]
]