from bs4 import BeautifulSoup
import requests
import logging
import re

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the headers once, outside the function
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Accept-Language': 'en-GB, en;q=0.5'
}

def fetch_attractions_data(location_id):
    base_url = f"https://www.tripadvisor.com.my/Attractions-{location_id}-Activities-oa0"
    logging.info(f"Fetching attractions data from URL: {base_url}")

    return scrape_attractions(base_url)

def scrape_attractions(base_url):
    url = base_url
    all_attractions = []

    while url and len(all_attractions) < 50:
        logging.info(f"Searching for attractions at: {url}")
        response = requests.get(url, headers=headers)
        logging.info(f"HTTP Status Code: {response.status_code}")

        if response.status_code != 200:
            logging.error("Failed to retrieve page, stopping scrape.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        current_page_attractions = parse_page(soup)
        all_attractions.extend(current_page_attractions[:max(0, 70 - len(all_attractions))])

        # Find the link to the next page if more attractions are needed
        if len(all_attractions) < 50:
            next_link = soup.find('a', {'aria-label': 'Next page'})
            url = 'https://www.tripadvisor.com' + next_link['href'] if next_link and 'href' in next_link.attrs else None

    return all_attractions

def parse_page(soup):
    attractions = soup.findAll('div', {'data-automation': 'cardWrapper'})  
    attractions_data = []

    for attraction in attractions:
        try:
            # Extract the name
            name_tag = attraction.find('h3', class_='biGQs')
            name = name_tag.get_text(strip=True) if name_tag else 'N/A'
            name = re.sub(r'^\d+\.\s*', '', name)  # Remove leading numbers

            # Extract the description
            description_tag = attraction.find('span', class_='yRoCR')
            if not description_tag:
                description_tag = attraction.find('span', class_='SwTtt')
            description = description_tag.get_text(strip=True) if description_tag else 'N/A'

            # Extract the category
            category_tag = attraction.find('div', class_='biGQs _P pZUbB hmDzD')
            category = category_tag.get_text(strip=True) if category_tag else 'N/A'

            # Extract the review count
            review_count_tag = attraction.find('span', class_='biGQs')
            review_count_text = review_count_tag.get_text(strip=True) if review_count_tag else 'N/A'
            review_count = int(review_count_text.replace(',', '')) if review_count_text != 'N/A' else 0

            # Extract the image URL
            image_tag = attraction.find('img')
            image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else 'N/A'

            # Extract the price
            price_tag = attraction.find('a', text=re.compile(r'Admission tickets from MYR'))
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                price_match = re.search(r'MYR\s*(\d+)', price_text)
                price = float(price_match.group(1)) if price_match else 0.0
            else:
                price = 0.0  # Default to 0.0 if price tag not found

            # Extract the link to the attraction's page
            place_link_element = attraction.find('a', {'href': True})
            place_link = 'https://www.tripadvisor.com' + place_link_element['href'] if place_link_element else 'N/A'

            # Extract the number of green bubbles (rating)
            rating_svg = attraction.find('svg', {'aria-labelledby': True})
            rating_text = rating_svg.find('title').text if rating_svg and rating_svg.find('title') else None
            
            number_of_green_bubbles = 0.0  # Default value
            if rating_text:
                rating_match = re.search(r'(\d+\.\d+|\d+) of 5 bubbles', rating_text)
                number_of_green_bubbles = float(rating_match.group(1)) if rating_match else 0.0

            # Append the attraction data
            attractions_data.append({
                'name': name,
                'category': category,
                'description': description,
                'review_count': review_count,
                'image_url': image_url,
                'price': price,
                'place_link': place_link,
                'number_of_green_bubbles': number_of_green_bubbles
            })
        except Exception as e:
            logging.error(f"Error processing attraction: {attraction}")
            logging.error(f"Error message: {e}")

    return attractions_data
