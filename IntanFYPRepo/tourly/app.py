from flask import Flask, render_template, request, jsonify, redirect, flash, session
from flask_session import Session  # Import for server-side sessions
import threading
import uuid
import mysql.connector
from datetime import datetime
from hotelscraper import fetch_hotels_data
from attractionscraper import fetch_attractions_data  # make sure this imports correctly
from restaurantscraper import fetch_restaurants_data  # new import for restaurant scraping
import logging
import re
import sqlite3
import time


app = Flask(__name__)

app.secret_key = 'intanfyp'  # Replace with a strong secret key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# Database configuration
db_config = {
    'user': 'root',                                                   
    'password': 'intanfyp',
    'host': 'localhost',
    'database': 'travelwebsite',
    'port': '3306'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

def parse_pax(pax):
    parts = pax.split(',')
    adults = int(parts[0].split()[0])
    rooms = int(parts[2].split()[0]) if len(parts) > 2 else 1
    return adults, rooms

def clean_price(price_str):
    # Remove all non-numeric characters except for the decimal point
    cleaned_price_str = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned_price_str)
    except ValueError:
        return None


def clean_rating(rating_str):
    try:
        return float(re.search(r'\d+\.\d+', rating_str).group(0))
    except (ValueError, AttributeError):
        return None

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Get data from the contact form
    custname = request.form['custname']
    email = request.form['email']
    message = request.form['message']

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # SQL query to insert data into the contactmessages table
        query = """
        INSERT INTO contactmessages (custname, email, message, submission_date)
        VALUES (%s, %s, %s, %s)
        """
        submission_date = datetime.now()
        values = (custname, email, message, submission_date)

        cursor.execute(query, values)
        conn.commit()

        flash("Thanks for contacting us. We'll get back to you as soon as possible.")
        return redirect('/contact.html')  # Redirect back to contact page after submission

    except Exception as e:
        app.logger.error(f"Error inserting contact message: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        cursor.close()
        conn.close()



@app.route('/search', methods=['POST'])
def search():
        
    try:    
        destination = request.form.get('destination')
        checkin_date = request.form.get('checkin_date')
        checkout_date = request.form.get('checkout_date')
        pax = request.form.get('pax')
        budget = request.form.get('budget')
        session_id = str(uuid.uuid4())  # Generate a new session_id


        logging.info(f"Received data - Destination: {destination}, Check-in Date: {checkin_date}, Check-out Date: {checkout_date}, Pax: {pax}, Budget: {budget}")

        if not all([destination, checkin_date, checkout_date, pax, budget]):
            logging.error(f"Error occurred: {str(e)}")

            return jsonify({"error": "All fields are required"}), 400

        try:
            datetime.strptime(checkin_date, '%Y-%m-%d')
            datetime.strptime(checkout_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        # Clean the budget string
        cleaned_budget = clean_price(budget)
        if cleaned_budget is None:
            return jsonify({"error": "Invalid budget format"}), 400

        adults, rooms = parse_pax(pax)
        total_pax = adults
        total_budget = cleaned_budget * total_pax

        # Calculate max accommodation budget
        max_accommodation_budget = total_budget * 0.30  # 30% of total budget

        # Start threads for scraping hotel data
        thread_hotel = threading.Thread(
            target=scrape_and_save_hotels, 
            args=(destination, checkin_date, checkout_date, adults, rooms, cleaned_budget, max_accommodation_budget, session_id)
        )
        thread_hotel.start()

        time.sleep(10)  # Adjust delay as needed, depending on scraping time


        # Redirect to results page with query parameters
        return redirect(f'/results/{session_id}?destination={destination}&checkin_date={checkin_date}&checkout_date={checkout_date}&pax={pax}&budget={budget}')

    except Exception as e:
        app.logger.error(f"Error occurred during search: {e}")
        # Return a response that does not trigger client-side alert
        return redirect('/results/<session_id>')

def scrape_and_save_hotels(destination, checkin_date, checkout_date, adults, rooms, budget, max_accommodation_budget, session_id):
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    logging.info(f"Starting scrape for {destination}")
    # Example call, replace 'booking' with dynamic source if needed
    
    try:
        cursor.execute("DELETE FROM accommodations")
        conn.commit()  # Commit the deletion of all rows

        logging.info("All old hotel data cleaned")

        hotels = fetch_hotels_data(destination, checkin_date, checkout_date, adults, rooms)
        logging.info(f"Number of hotels fetched: {len(hotels)}")

        for hotel in hotels:
            clean_price_value = clean_price(hotel['price'])
            if clean_price_value <= max_accommodation_budget:  # Filtering logic here
                cursor.execute(
                    """
                    INSERT INTO accommodations 
                    (name, location, price, rating, session_id, check_in, check_out, pax, budget, image_url, room_info, source, hotel_link) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (hotel['name'], hotel['location'], clean_price_value, hotel['rating'], session_id, checkin_date, checkout_date, f"{adults} adults, {rooms} rooms", budget, hotel['image_url'], hotel['room_info'], hotel['source'], hotel['hotel_link'])
                )
        conn.commit()
        logging.info("Data committed to database")
    except Exception as e:
        app.logger.error(f"Database insertion error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

"""
def scrape_and_save_attractions(destination, session_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attractions")
    conn.commit()  # Commit the deletion of all rows

    logging.info("All old attractions data cleaned")

    try:
        # Assume destination is correctly passed to fetch the location_id
        cursor.execute("SELECT LocationID FROM LocationIDs WHERE PlaceName = %s", (destination,))
        locationid_result = cursor.fetchone()
        if locationid_result:
            locationid = locationid_result[0]
            attractions = fetch_attractions_data(locationid)
            for attraction in attractions:
                # Convert and validate review_count
                try:
                    review_count = int(attraction.get('review_count', 0))
                except ValueError:
                    review_count = 0  # Default to 0 if conversion fails
                
                # Log the data just before insertion
                logging.info(f"Inserting attraction with review_count: {review_count}")

                cursor.execute(
                    #trip aphost
                    INSERT INTO attractions (name, description, category, review_count, locationid, price, number_of_green_bubbles, image_url, place_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    description = VALUES(description),
                    review_count = VALUES(review_count),
                    price = VALUES(price),
                    number_of_green_bubbles = VALUES(number_of_green_bubbles),
                    image_url = VALUES(image_url),
                    place_link = VALUES(place_link)
                    #triple aphost,
                    (attraction['name'], attraction['description'], attraction['category'], review_count, locationid,
                     attraction.get('price', 0.0), attraction.get('number_of_green_bubbles', 0), attraction.get('image_url', ''),
                     attraction.get('place_link', ''))
                )
            conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"Error during attraction data scraping: {e}")
    finally:
        cursor.close()
        conn.close()

# New function for scraping and saving restaurant data

def scrape_and_save_restaurants(destination, session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, fetch the location ID for the destination
        cursor.execute("SELECT LocationID FROM LocationIDs WHERE PlaceName = %s", (destination,))
        locationid_result = cursor.fetchone()

        if locationid_result:
            locationid = locationid_result[0]
            restaurants = fetch_restaurants_data(locationid)  # Fetch restaurants using the location ID

            for restaurant in restaurants:
                clean_price_value = clean_price(restaurant.get('price', ''))
                cursor.execute(
                    #adathreedoubleephortophy
                    INSERT INTO restaurants 
                    (name, category, number_of_green_bubbles, review_count, price, image_url, restaurant_url, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    #adathreedoubleephortophy,
                    (restaurant['name'], restaurant['category'], restaurant['number_of_green_bubbles'],
                    restaurant['review_count'], clean_price_value, restaurant['image_url'], restaurant['restaurant_url'], session_id)
                )
            conn.commit()
            logging.info("Restaurant data committed to the database")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error inserting restaurant data: {e}")
    finally:
        cursor.close()
        conn.close()
"""

@app.route('/results/<session_id>')
def results(session_id):
    destination = request.args.get('destination')
    checkin_date = request.args.get('checkin_date')
    checkout_date = request.args.get('checkout_date')
    pax = request.args.get('pax')
    budget = request.args.get('budget')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        logging.info(f"Fetching results for session_id: {session_id}")

        # Fetch accommodations with a rating of at least 5.0
        cursor.execute("""
        SELECT name, location, price, rating, room_info, image_url, hotel_link
        FROM accommodations
        WHERE session_id = %s 
        AND price IS NOT NULL 
        AND rating IS NOT NULL 
        AND rating >= 5.0
        AND room_info IS NOT NULL 
        AND room_info != 'Details not available'
        ORDER BY price ASC, rating DESC
        """, (session_id,))
        hotels = cursor.fetchall()


        # Fetch attractions
        cursor.execute("""
        SELECT name, description, category, review_count, image_url, place_link, number_of_green_bubbles 
        FROM backupattractions
        WHERE location = %s 
        AND description IS NOT NULL AND description != 'N/A'
        AND review_count IS NOT NULL AND number_of_green_bubbles IS NOT NULL
        ORDER BY review_count DESC, number_of_green_bubbles DESC
        """, (destination,))
        attractions = cursor.fetchall()

        # Fetch restaurants
        cursor.execute("""
        SELECT name, category, number_of_green_bubbles, review_count, price_point, image_url, restaurant_url
        FROM backuprestaurants
        WHERE location = %s AND review_count IS NOT NULL
        ORDER BY number_of_green_bubbles DESC, review_count DESC,
        CASE 
            WHEN price_point = '$' THEN 1
            WHEN price_point = '$$ - $$$' THEN 2
            WHEN price_point = '$$$$' THEN 3
            ELSE 4
        END ASC
        """, (destination,))
        restaurants = cursor.fetchall()

        # Add image_url and place_link to the results dictionary for hotels
        results = {
            'hotels': [{'name': h[0], 'location': h[1], 'price': h[2], 'rating': h[3], 'room_info': h[4], 'image_url': h[5], 'hotel_link': h[6]} for h in hotels],
            'attractions': [{'name': a[0], 'description': a[1], 'category': a[2], 'review_count': a[3], 'image_url': a[4], 'place_link': a[5], 'number_of_green_bubbles': a[6]} for a in attractions],
            'restaurants': [{'name': r[0], 'category': r[1], 'number_of_green_bubbles': r[2], 'review_count': r[3], 'price_point': r[4], 'image_url': r[5], 'restaurant_url': r[6]} for r in restaurants]
        }

        # Pass the retrieved variables to the template
        return render_template(
            'results.html',
            results=results,
            session_id=session_id,
            destination=destination,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            pax=pax,
            budget=budget
        )

    except Exception as e:
        app.logger.error(f"Error retrieving results: {e}")
        return render_template('error.html', error_message='Error retrieving results, please try again later.')
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
