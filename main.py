#main.py
from Eposcraper import EpoScraper
from Wiposcraper import WipoScraper
from Jposcraper import JpoScraper

if __name__ == "__main__":
    search_term = input("Enter search term: ")
    # search_term = "mobile"
    chromedriver_path = './chromedriver/chromedriver.exe'
    # scraper = WipoScraper(chromedriver_path)
    # scraper.scrape_patents(search_term)
    scraper = JpoScraper(chromedriver_path)
    scraper.scrape_patents(search_term)
    scraper = EpoScraper(chromedriver_path)
    scraper.scrape_patents(search_term)
