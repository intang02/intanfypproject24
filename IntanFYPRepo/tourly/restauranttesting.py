from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the headers once, outside the function
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}



def fetch_restaurants_data(page_url):
    logging.info(f"Searching for URL for destination: {page_url}")

    response = requests.get(page_url, headers=headers)
    response = requests.get(url, headers=headers)
    logging.info(f"HTML snippet: {response.text[:500]}")  # Log the first 500 characters of the response to check content

    logging.info(f"HTTP Status Code: {response.status_code}")
    logging.info(f"Response URL: {response.url}")


    soup = BeautifulSoup(response.text, 'html.parser')
    restaurants_data = []

    restaurants = soup.findAll('div', {'data-automation': 'cardWrapper'})  # Adjust class name as needed based on TripAdvisor's layout
    count = 0

    for restaurant in restaurants:
        if count >= 70:
            break
        try:
            name = restaurant.find('a', class_='VDEXx u Ff K').text.strip() if restaurant.find('a', class_='VDEXx u Ff K') else 'N/A'
            category = restaurant.find('span', class_='YECgr Tsrjt').get_text(strip=True) if restaurant.find('span', class_='YECgr Tsrjt') else 'N/A'
            #description = restaurant.find('div', class_='biGQs _P pZUbB KxBGd').text.strip() if attraction.find('div', class_='biGQs _P pZUbB KxBGd') else 'N/A'
            #review_count = restaurant.find('span', class_='biGQs _P pZUbB osNWb').text.strip() if attraction.find('span', class_='biGQs _P pZUbB osNWb') else 'N/A'

            restaurants_data.append({
                'name': name, 
                #'description': description, 
                'category': category, 
                #'review_count': review_count
                })
            
            count += 1

        except Exception as e:
            print(f"Error processing restaurant: {restaurant}")
            print(f"Error message: {e}")
        
    return restaurants_data

# Start URL
url = 'https://www.tripadvisor.com.my/Restaurants-g660694-oa0.html'

all_restaurants = []
while url and len(all_restaurants) < 70:
    current_page_restaurants = fetch_restaurants_data(url)
    all_restaurants.extend(current_page_restaurants[:max(0, 70 - len(all_restaurants))])  # Prevent adding more than 70
    
    # Find the link to the next page if more attractions are needed
    if len(all_restaurants) < 70:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
        next_link = soup.find('a', {'aria-label': 'Next page'})
        if next_link and 'href' in next_link.attrs:
            url = 'https://www.tripadvisor.com.my' + next_link['href']
        else:
            url = None  # Stop loop if no next page is found or 70 attractions are collected

# Create DataFrame from the extracted data
df_restaurants = pd.DataFrame(all_restaurants)
print(df_restaurants.head(25))
print(f'Total restaurants scraped: {len(df_restaurants)}')
