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


@dataclass
class EpoPatent:
    patent_number: str
    title: str = None
    applicants: list = None
    inventors: list = None
    application_number: str = None
    publication_number: str = None
    application_date: datetime.date = None
    publication_date: datetime.date = None
    abstract: str = None

class EpoScraper:
    def __init__(self, chromedriver_path):
        self.driver = self.initialize_driver(chromedriver_path)

    def initialize_driver(self, chromedriver_path):
        # Create a service object with the path to chromedriver
        service = Service(chromedriver_path)
        # Initialize the WebDriver
        return webdriver.Chrome(service=service)

    def open_espacenet(self):
        self.driver.get('https://worldwide.espacenet.com/')
        time.sleep(2)

    def search_patents(self, search_term):
        search_box_selector = 'input[aria-label="Search" i][type="search" i]'
        element = self.driver.find_element(By.CSS_SELECTOR, search_box_selector)
        element.send_keys(search_term)
        element.send_keys(Keys.RETURN)
        time.sleep(5)  # Adjust the sleep time as needed to allow for the search results to load

    def get_article_headers(self):
        return self.driver.find_elements(By.XPATH, '//article//header')

    def click_hide_result_list(self):
        svg_hide_search = self.driver.find_element(By.XPATH, '//div[translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="hide result list"]//button')
        svg_hide_search.click()

    def click_show_result_list(self):
        svg_show_search = self.driver.find_element(By.XPATH, '//div[translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="show result list"]//button')
        svg_show_search.click()

    def extract_patent_data(self):
        try:
            title = self.driver.find_element(By.ID, 'biblio-title-content').text
        except NoSuchElementException:
            title = None

        try:
            applicants_text = self.driver.find_element(By.XPATH, '//span[@id="biblio-applicants-content"]').text
            applicants = [applicant.strip() for applicant in applicants_text.split(';')]
        except NoSuchElementException:
            applicants = []

        try:
            inventors_text = self.driver.find_element(By.XPATH, '//span[@id="biblio-inventors-content"]').text
            inventors = [inventor.strip() for inventor in inventors_text.split(';')]
        except NoSuchElementException:
            inventors = []

        try:
            application = self.driver.find_element(By.XPATH, '//span[@id="biblio-application-number-content"]').text
            application_number, application_date_str = application.split('·')
            try:
                application_date = datetime.datetime.strptime(application_date_str.strip(), '%Y-%m-%d').date()
            except ValueError:
                application_date = None    
        except NoSuchElementException:
            application_number = None
            application_date = None

        try:
            publication = self.driver.find_element(By.XPATH, '//span[@id="biblio-publication-number-content"]').text
            publication_number, publication_date_str = publication.split('·')
            try:
                publication_date = datetime.datetime.strptime(publication_date_str.strip(), '%Y-%m-%d').date()
            except ValueError:
                publication_date = None
        except NoSuchElementException:
            publication_number = None
            publication_date = None

        try:
            abstract = self.driver.find_element(By.XPATH, '//div[@id="biblio-abstract-content"]//p').text
        except NoSuchElementException:
            abstract = None

        return EpoPatent(
            patent_number=application_number,
            title=title,
            applicants=applicants,
            inventors=inventors,
            application_number=application_number,
            publication_number=publication_number,
            application_date=application_date,
            publication_date=publication_date,
            abstract=abstract
            )

    def save_patent_to_db(self, patent_data):
        if patent_data.patent_number:
            existing_patent = MongoPatent.objects(patent_number=patent_data.patent_number).first()
            if not existing_patent:
                patent = MongoPatent(**asdict(patent_data))
                patent.save()

    def scrape_patents(self,search_term):

        self.open_espacenet()
        self.search_patents(search_term)

        article_headers = self.get_article_headers()
        for i in range(len(article_headers)):
            article_headers = self.get_article_headers()
            article_headers[i].click()
            self.click_hide_result_list()
            time.sleep(2)  # Adjust the sleep time as needed to allow for the search results to load

            patent_data = self.extract_patent_data()
            self.save_patent_to_db(patent_data)

            self.click_show_result_list()
            time.sleep(2)  # Adjust the sleep time as needed to allow for the search results to load

        self.driver.quit()
