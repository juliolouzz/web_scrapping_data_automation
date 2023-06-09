import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import requests

GOOGLE_FORM_LINK = ""  # your google forms with 3 questions / short aswers
WEBSITE_HTML_ZILLOW = "https://www.zillow.com/" # your url with your own parameters to find houses
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 "
                  "Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Send a GET request to Zillow website and retrieve the HTML response
response = requests.get(url=WEBSITE_HTML_ZILLOW, headers=header)
ZILLOW_TEXT = response.text

# Parse the HTML response using BeautifulSoup
soup = BeautifulSoup(ZILLOW_TEXT, "lxml")

# Find all script tags with type "application/json" in the HTML response
test = soup.find_all("script", attrs={"type": "application/json"})
# print(len(test)) # to see how many tags, and print to see each one when you extract the content.

# Extract the text content of the second script tag
rent_data = test[1].text

# Remove HTML comments from the text content
rent_data = rent_data.replace("<!--", "")
rent_data = rent_data.replace("-->", "")

# Load the JSON data from the extracted text
rent_data = json.loads(rent_data)

# Extract the URLs of the rental listings from the JSON data
link_list = []
for i in rent_data["cat1"]["searchResults"]["listResults"]:
    link = i["detailUrl"]
    link_list.append(link)

# Make sure all URLs start with "https"
for i in range(len(link_list)):
    if not link_list[i].startswith("https"):
        link_list[i] = "https://www.zillow.com" + link_list[i]

# Extract the prices of the rental listings from the JSON data
price_list = []
for i in rent_data["cat1"]["searchResults"]["listResults"]:
    try:
        price = i["price"]
        price_list.append(price)
    except KeyError:
        price = i["units"][0]["price"]
        price_list.append(price)

# Extract only the first 6 characters from the prices (to remove additional information)
new_price_list = []
for new in price_list:
    print(type(new))
    new_price_list.append(new[:6])

# Update the price list with the shortened prices
price_list = new_price_list
print(price_list)

# Extract the addresses of the rental listings from the JSON data
address_list = []
for i in rent_data["cat1"]["searchResults"]["listResults"]:
    address = i["address"]
    address_list.append(address)

# Initialize a Selenium webdriver for Chrome
driver = webdriver.Chrome()

# Iterate through the link list and fill out the Google Form with address, price, and link for each rental listing
for i in range(len(link_list)):
    driver.get(GOOGLE_FORM_LINK)
    time.sleep(1)
    question_1 = driver.find_elements(By.CSS_SELECTOR, "div.Xb9hP input")[0]
    question_1.send_keys(address_list[i])

    question_2 = driver.find_elements(By.CSS_SELECTOR, "div.Xb9hP input")[1]
    question_2.send_keys(price_list[i])

    question_3 = driver.find_elements(By.CSS_SELECTOR, "div.Xb9hP input")[2]
    question_3.send_keys(link_list[i])

    submit = driver.find_element(By.CSS_SELECTOR, "div.lRwqcd div")
    submit.click()

