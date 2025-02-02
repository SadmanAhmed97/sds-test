from selenium import webdriver
from selenium.webdriver.common.by import By
import time, scrapy, psycopg2

driver = webdriver.Chrome()

class BookingSpider(scrapy.Spider):
    name = 'booking'
    allowed_domains = ['www.booking.com/']
    start_urls = ["https://www.booking.com/"]

    driver.get("https://www.booking.com/city/bd/coxs-bazar.html")

    def parse(self, response):
        driver.maximize_window()
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_increment = 80 
        scroll_delay = 0.1      
        scroll_position = 0
        while scroll_position < page_height:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(scroll_delay)
            scroll_position += scroll_increment
            
        hotel_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="card"]')

        for hotel_card in hotel_cards:
            try:
                hotel_name = hotel_card.find_element(By.CSS_SELECTOR, '[data-testid="title"]').text
                
                image_element = hotel_card.find_element(By.CSS_SELECTOR, '[data-testid="image"]')
                image_link = image_element.get_attribute("src")
                
                try:
                    stars = len(hotel_card.find_elements(By.CSS_SELECTOR, "div.b9bf9fafbf span"))
                except:
                    stars = "No star rating"

                try:
                    price = hotel_card.find_element(By.CSS_SELECTOR, '.d746e3a28e').text
                except:
                    price = "Price not available"

                booking_url = hotel_card.find_element(By.CSS_SELECTOR, '[data-testid="titleLink"]').get_attribute("href")
                current_url = driver.current_url

                self.store_in_db(hotel_name, image_link, stars, price, booking_url, current_url)

            except Exception as e:
                print("Error extracting data:", e)

        driver.quit()

    def store_in_db(self, name, image, stars, price, booking_url, current_url):
        conn = psycopg2.connect(
            dbname="SDS", user="postgres", password="Sadman@123", host="localhost", port="5432"
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO public.hotels_bookingdotcom(name, image, stars, price, booking_url, current_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, image, stars, price, booking_url, current_url),
        )
        
        conn.commit()
        cursor.close()
        conn.close()



