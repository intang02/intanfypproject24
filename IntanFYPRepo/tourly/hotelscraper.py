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

def clean_rating(rating_str):
    """Extracts the numeric rating from a string, or returns None if not possible."""
    try:
        return float(re.search(r'\d+\.\d+', rating_str).group(0))
    except (ValueError, AttributeError):
        return None

def fetch_hotels_data(destination, checkin, checkout, adults, rooms):
    """Fetches hotel data from Booking.com based on given search criteria, for both price and review score sorting."""
    urls = {
        'price_sorted': f'https://www.booking.com/searchresults.html?ss={destination}&checkin={checkin}&checkout={checkout}&group_adults={adults}&no_rooms={rooms}&order=price',
        'review_and_price_sorted': f'https://www.booking.com/searchresults.html?ss={destination}&checkin={checkin}&checkout={checkout}&group_adults={adults}&no_rooms={rooms}&order=review_score_and_price',
    }

    all_hotels = []
    for source, url in urls.items():
        logging.info(f"Requesting URL for {source}: {url}")
        response = requests.get(url, headers=headers)
        logging.info(f"Response URL: {response.url}")

        if response.status_code == 200:
            hotels = parse_hotels(response.text, source, url)
            all_hotels.extend(hotels)  # Collect all hotel data
        else:
            logging.error(f"Failed to fetch data from {url} (Status Code: {response.status_code})")

    # Remove potential duplicates by a unique identifier, e.g., hotel link
    unique_hotels = {hotel['hotel_link']: hotel for hotel in all_hotels}.values()
    return list(unique_hotels)


def parse_hotels(html_content, source, base_url):
    """Parses hotel data from HTML content based on the source."""
    soup = BeautifulSoup(html_content, 'html.parser')
    hotels_data = []

    hotels = soup.findAll('div', {'data-testid': 'property-card'})
    for hotel in hotels:
        hotels_data.append(extract_booking_details(hotel, base_url))

    return hotels_data

def extract_booking_details(hotel, base_url):
    """Extract specific details for Booking.com."""
    name = hotel.find('div', {'data-testid': 'title'}).text.strip()
    location = hotel.find('span', {'data-testid': 'address'}).text.strip()
    price = hotel.find('span', {'data-testid': 'price-and-discounted-price'}).text.strip()

    rating_element = hotel.find('div', {'class': 'a3b8729ab1 d86cee9b25'})
    rating = clean_rating(rating_element.text.strip()) if rating_element else None

    # Extracting the correct hotel link
    hotel_link_element = hotel.find('a', {'data-testid': 'title-link'})
    hotel_link = hotel_link_element['href'] if hotel_link_element else None
    full_link = f"{hotel_link}" if hotel_link else 'N/A'

    image_element = hotel.find('img', {'data-testid': 'image'})

    image_url = image_element['src'] if image_element else 'N/A'

    room_info = hotel.find('div', {'class': 'c59cd18527'}).text.strip() if hotel.find('div', {'class': 'c59cd18527'}) else 'Details not available'
    
    return {
        'name': name,
        'location': location,
        'price': price,
        'rating': rating,
        'image_url': image_url,
        'room_info': room_info,
        'source': 'booking.com',
        'hotel_link': full_link
    }


