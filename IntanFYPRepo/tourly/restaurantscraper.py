from bs4 import BeautifulSoup
import requests
import logging
import re
import time
import random

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the headers once, outside the function
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Accept-Language': 'en-GB, en;q=0.5'
}

def fetch_restaurants_data(location_id):
    base_url = f"https://www.tripadvisor.com.my/Restaurants-{location_id}-oa0"
    logging.info(f"Fetching restaurants data from URL: {base_url}")
    
    return scrape_restaurants(base_url)

def scrape_restaurants(base_url):
    url = base_url
    all_restaurants = []

    while url and len(all_restaurants) < 5:  # Change to scrape only up to 30 restaurants
        logging.info(f"Searching for restaurants at: {url}")
        response = requests.get(url, headers=headers)
        logging.info(f"HTTP Status Code: {response.status_code}")

        if response.status_code != 200:
            logging.error("Failed to retrieve page, stopping scrape.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        current_page_restaurants = parse_page(soup)
        all_restaurants.extend(current_page_restaurants[:max(0, 5 - len(all_restaurants))])  # Ensure no more than 30

        logging.info(f"Scraped {len(current_page_restaurants)} restaurants on this page.")  # Log how many were scraped

        # Find the link to the next page if more restaurants are needed
        if len(all_restaurants) < 5:
            next_link = soup.find('a', {'aria-label': 'Next page'})
            url = 'https://www.tripadvisor.com.my' + next_link['href'] if next_link and 'href' in next_link.attrs else None

    logging.info(f"Total restaurants scraped: {len(all_restaurants)}")  # Log the total number scraped
    return all_restaurants

def parse_page(soup):
    restaurants_data = []
    restaurants = soup.findAll('div', {'class': 'WlYyy cspKb dAdhB'})  # Ensure this is the correct container class

    for restaurant in restaurants:
        try:
            # Extracting details as before, ensure these match the HTML structure
            name = restaurant.find('div', class_='biGQs _P fiohW alXOW NwcxK GzNcM ytVPx UTQMg RnEEZ ngXxk').get_text(strip=True) if restaurant.find('div', class_='biGQs _P fiohW alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU mtnKn ngXxk') else 'N/A'
            category = restaurant.find('span', class_='YECgr Tsrjt').get_text(strip=True) if restaurant.find('div', class_='YECgr Tsrjt') else 'N/A'
            #rating_svg = restaurant.find('svg', class_='UctUV d H0 hzzSG')
            #rating_text = rating_svg.parent.find('span', class_='biGQs _P pZUbB osNWb').get_text(strip=True) if rating_svg else 'N/A'
            #review_count = rating_svg.parent.find('span', class_='yyzcQ').get_text(strip=True) if rating_svg else 'N/A'
            #price = restaurant.find('span', class_='f').get_text(strip=True) if restaurant.find('span', class_='f') else 'N/A'
            #image_url = restaurant.find('img')['src'] if restaurant.find('img') else 'N/A'
            #restaurant_link = 'https://www.tripadvisor.com.my' + restaurant.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')['href'] if restaurant.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS') else 'N/A'

            # Append restaurant data
            restaurants_data.append({
                'name': name,
                'category': category,
                #'number_of_green_bubbles': rating_text.split()[0] if rating_text else 'N/A',
                #'review_count': review_count,
                #'price': price,
                #'image_url': image_url,
                #'restaurant_url': restaurant_link
            })

        except Exception as e:
            logging.error(f"Error processing restaurant data: {e}")

    return restaurants_data
