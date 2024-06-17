#scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import datetime
import time
from db import MongoPatent
from mongoengine import connect
from dataclasses import dataclass, asdict
from selenium.webdriver.chrome.options import Options



@dataclass
class JpoPatent:
    patent_number: str
    title: str = None
    applicants: list = None
    inventors: list = None
    application_number: str = None
    publication_number: str = None
    application_date: datetime.date = None
    publication_date: datetime.date = None
    abstract: str = None

class JpoScraper:
    def __init__(self, chromedriver_path):
        self.driver = self.initialize_driver(chromedriver_path)

    def initialize_driver(self, chromedriver_path):
        # Create a service object with the path to chromedriver
        service = Service(chromedriver_path)
        chrome_options = Options()
        chrome_options.add_argument("--lang=en")  # Set English language
        # Initialize the WebDriver
        return webdriver.Chrome(service=service, options=chrome_options)

    def open_jplatpat(self):
        self.driver.get('https://www.j-platpat.inpit.go.jp/')
 

        time.sleep(2)
        self.driver.find_element(By.XPATH, '//a[text()="English"]').click() 

    def search_patents(self, search_term):

        element = self.driver.find_element(By.XPATH, '//input[contains(@id, "SimpleSearch")]')
        # search_box_selector = 'input[aria-label="Search" i][type="search" i]'
        # element = self.driver.find_element(By.CSS_SELECTOR, search_box_selector)
        element.send_keys(search_term)
        element = self.driver.find_element(By.XPATH, '//span[text()="Search"]')
        element.click()
        # element.send_keys(Keys.RETURN)
        time.sleep(10)  # Adjust the sleep time as needed to allow for the search results to load
        # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//article//header')))


    def get_article_headers(self):
        return self.driver.find_elements(By.XPATH, '//article//header')

    # def click_hide_result_list(self):
    #     svg_hide_search = self.driver.find_element(By.XPATH, '//div[translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="hide result list"]//button')
    #     svg_hide_search.click()

    # def click_show_result_list(self):
    #     svg_show_search = self.driver.find_element(By.XPATH, '//div[translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="show result list"]//button')
    #     svg_show_search.click()

    def extract_patent_data(self, row):
        pub_num = row.find_element(By.XPATH, './/td[@id="patentUtltyIntnlSimpleBibLst_tableView_docNumArea"]/p/a').text.strip()
        app_num = row.find_element(By.XPATH, './/td[@id="patentUtltyIntnlSimpleBibLst_tableView_appNumArea"]/p').text.strip()
        app_date = row.find_element(By.XPATH, './/td[@id="patentUtltyIntnlSimpleBibLst_tableView_appDateArea"]/p').text.strip()
        pub_date = row.find_element(By.XPATH, './/td[@id="patentUtltyIntnlSimpleBibLst_tableView_knowDateArea"]/p').text.strip()
        title = row.find_element(By.XPATH, './/td[@id="patentUtltyIntnlSimpleBibLst_tableView_invenNameArea"]/p').text.strip()
        applicant = row.find_element(By.XPATH, './/td[@id="patentUtltyIntnlSimpleBibLst_tableView_appnRightHolderArea"]/p').text.strip()

        
        return JpoPatent(
            patent_number=app_num,
            title=title,
            applicants=[applicant],
            # inventors=inventors,
            application_number=app_num,
            publication_number=pub_num,
            application_date=app_date,
            publication_date=pub_date,
            # abstract=abstract
            )

    def save_patent_to_db(self, patent_data):
        if patent_data.patent_number:
            existing_patent = MongoPatent.objects(patent_number=patent_data.patent_number).first()
            if not existing_patent:
                patent = MongoPatent(**asdict(patent_data))
                patent.save()

    def scrape_patents(self,search_term):

        self.open_jplatpat()
        self.search_patents(search_term)

        rows = self.driver.find_elements(By.XPATH, '//tr[contains(@id, "patentUtltyIntnlSimpleBibLst_tableView")]')
        for i in range(len(rows)):
            
            time.sleep(2)  # Adjust the sleep time as needed to allow for the search results to load

            patent_data = self.extract_patent_data(rows[i])
            self.save_patent_to_db(patent_data)

            time.sleep(2)  # Adjust the sleep time as needed to allow for the search results to load

        self.driver.quit()
