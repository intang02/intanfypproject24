from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the headers once, outside the function
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Accept-Language': 'en-GB, en;q=0.5'
}

def fetch_attractions_data(page_url):
    logging.info(f"Searching for URL for destination: {page_url}")

    response = requests.get(page_url, headers=headers)
    logging.info(f"HTTP Status Code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    attractions_data = []

    attractions = soup.findAll('div', {'data-automation': 'cardWrapper'})  # Adjust class name as needed based on TripAdvisor's layout
    count = 0

    for attraction in attractions:
        if count >= 70:
            break
        try:
            name = attraction.find('div', class_='XfVdV o AIbhI').text.strip() if attraction.find('div', class_='XfVdV o AIbhI') else 'N/A'
            category = attraction.find('div', class_='biGQs _P pZUbB hmDzD').text.strip() if attraction.find('div', class_='biGQs _P pZUbB hmDzD') else 'N/A'
            description = attraction.find('div', class_='biGQs _P pZUbB KxBGd').text.strip() if attraction.find('div', class_='biGQs _P pZUbB KxBGd') else 'N/A'
            review_count = attraction.find('span', class_='biGQs _P pZUbB osNWb').text.strip() if attraction.find('span', class_='biGQs _P pZUbB osNWb') else 'N/A'

            attractions_data.append({
                'name': name, 
                'description': description, 
                'category': category, 
                'review_count': review_count})
            
            count += 1

        except Exception as e:
            print(f"Error processing attraction: {attraction}")
            print(f"Error message: {e}")
        
    return attractions_data

# Start URL
url = 'https://www.tripadvisor.com/Attractions-g298302-Activities-oa0-Penang.html'

all_attractions = []
while url and len(all_attractions) < 70:
    current_page_attractions = fetch_attractions_data(url)
    all_attractions.extend(current_page_attractions[:max(0, 70 - len(all_attractions))])  # Prevent adding more than 70
    
    # Find the link to the next page if more attractions are needed
    if len(all_attractions) < 70:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
        next_link = soup.find('a', {'aria-label': 'Next page'})
        if next_link and 'href' in next_link.attrs:
            url = 'https://www.tripadvisor.com' + next_link['href']
        else:
            url = None  # Stop loop if no next page is found or 70 attractions are collected

# Create DataFrame from the extracted data
df_attractions = pd.DataFrame(all_attractions)
print(df_attractions.head(25))
print(f'Total attractions scraped: {len(df_attractions)}')
