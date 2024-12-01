import sys
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# default path to file to store data
path_to_file = "/Users/gius/Desktop/restaurants.csv"

# default number of scraped pages
num_page = 10

# default TripAdvisor website of restaurants
url = 'https://www.tripadvisor.com.my/Restaurants-g660694-oa0.html'

# if you pass the inputs in the command line
if len(sys.argv) == 4:
    path_to_file = sys.argv[1]
    num_page = int(sys.argv[2])
    url = sys.argv[3]

# Setup WebDriver
driver = webdriver.Safari()  # Consider using Chrome or Firefox with appropriate drivers if Safari is not configured
driver.get(url)

# Open the file to save the restaurant data
with open(path_to_file, 'a', newline='', encoding="utf-8") as csvFile:
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(["Restaurant Name", "Category"])  # Writing header row

    for i in range(0, num_page):
        time.sleep(2)  # Wait for the dynamic content to load
        
        # Get all restaurant blocks on the current page
        restaurants = driver.find_elements(By.XPATH, "//div[@data-test='list_item']")

        for restaurant in restaurants:
            try:
                # Extract restaurant name
                name = restaurant.find_element(By.XPATH, ".//a[contains(@class,'_S')]").text
                # Extract category (assuming it's available directly following the name element)
                category = restaurant.find_element(By.XPATH, ".//span[@class='YECgr Tsrjt']").text

                # Write to CSV
                csvWriter.writerow([name, category])
            except Exception as e:
                print(f"Error extracting data: {e}")

        # Attempt to go to the next page
        try:
            next_button = driver.find_element(By.XPATH, './/a[@class="nav next ui_button primary"]')
            next_button.click()
        except Exception:
            print("No more pages or unable to click next.")
            break

driver.quit()  # Properly close the driver
