from selenium import webdriver
from selenium.webdriver.common.by import By
import time, scrapy, psycopg2
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


driver = webdriver.Chrome()

class BookingSpider(scrapy.Spider):
    name = 'agoda'
    allowed_domains = ['www.agoda.com/']
    start_urls = ["https://www.agoda.com/"]

    def parse(self, response):
        driver.get("https://www.agoda.com/search?city=671817&locale=en-us&ckuid=fae7f90e-c63b-4ff9-bc7d-5ecdf518dc2f&prid=0&gclid=Cj0KCQiAhvK8BhDfARIsABsPy4jjNNBbE8Pq7cnM9R5kbhAre5Wdwx8fZrj2YHfN2EllGxOsqptwiDoaAlVHEALw_wcB&currency=BDT&correlationId=1dfc8a5a-0bf8-4dda-9435-504d4e2c0f5e&analyticsSessionId=7328672040584853592&pageTypeId=1&realLanguageId=1&languageId=1&origin=BD&stateCode=13&cid=1922890&tag=56607b72-e9a1-472a-8654-4037959dedf1&userId=fae7f90e-c63b-4ff9-bc7d-5ecdf518dc2f&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=169&currencyCode=BDT&htmlLanguage=en-us&cultureInfoName=en-us&machineName=sg-pc-6h-acm-web-user-649c8c98fc-thxvw&trafficGroupId=5&trafficSubGroupId=122&aid=82361&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&browserFamily=Chrome&cdnDomain=agoda.net&checkIn=2025-02-07&checkOut=2025-02-08&rooms=1&adults=2&children=0&priceCur=BDT&los=1&textToSearch=Cox%27s+Bazar&travellerType=1&familyMode=off&ds=FAEXu2BYEMK4mELN&productType=-1")
        driver.maximize_window()
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_increment = 80 
        scroll_delay = 0.1      
        scroll_position = 0
        while scroll_position < page_height:
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(scroll_delay)
            scroll_position += scroll_increment
            
        hotel_cards = driver.find_elements(By.CSS_SELECTOR, '[data-selenium="hotel-item"]')

        print("Hotel Cards:", hotel_cards)

        for hotel_card in hotel_cards:
            try:
                hotel_name = hotel_card.find_element(By.CSS_SELECTOR, '[data-selenium="hotel-name"]').text
                # print(hotel_name)
                image_element = hotel_card.find_element(By.CSS_SELECTOR, ".Overlay img")
                srcset = image_element.get_attribute("srcset")
                # image_url = srcset.split(",")[0].split(" ")[0] if srcset else image_element.get_attribute("src")
                try:
                    star_locater = WebDriverWait(hotel_card, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.aff5b-box.aff5b-fill-inherit.aff5b-text-inherit.aff5b-flex')))
                    stars_text = star_locater.find_element(By.TAG_NAME, "span").text
                    stars = self.extract_stars(stars_text)
                except:
                    stars = 0

                try:
                    price = hotel_card.find_element(By.CSS_SELECTOR, "[data-selenium='display-price']").text
                except:
                    price = 0

                hotel_link_element = hotel_card.find_element(By.CSS_SELECTOR, ".PropertyCard__Link")
                hotel_link = hotel_link_element.get_attribute("href")
                current_url = driver.current_url

                self.store_in_db(hotel_name, srcset, stars, price, hotel_link, current_url)
                
            except Exception as e:
                print("Error extracting data:", e)

        driver.quit()

    def extract_stars(self, text):
        import re
        match = re.search(r'(\d+) stars out of 5', text)
        return int(match.group(1)) if match else 0
    
    def store_in_db(self, name, image, stars, price, booking_url, current_url):
        conn = psycopg2.connect(
            dbname="SDS", user="postgres", password="Sadman@123", host="localhost", port="5432"
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO public.hotels_agoda(name, image, stars, price, booking_url, current_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, image, stars, price, booking_url, current_url),
        )
        
        conn.commit()
        cursor.close()
        conn.close()



