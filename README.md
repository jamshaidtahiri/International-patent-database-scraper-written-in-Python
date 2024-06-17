International patent database scraper written in Python
Posted 2 weeks ago

#BELOW WAS FREELANCE TASK
#SAMPLE CODE IS ATTACHED IN THIS REPO

List of patent databases need to be scraped:

1. Europe: https://www.epo.org/en/searching-for-patents/technical/espacenet
2. Japan: https://www.j-platpat.inpit.go.jp/
3. PCT: https://www.wipo.int/patentscope/en/
4. China: https://english.cnipa.gov.cn/
5. Korea: https://www.kipo.go.kr/en/MainApp?c=1000

We're looking to break this project up into milestones, each of which correspond to one of the data sources listed above.

Technical requirements:
- Written in Python 3.12
- Deployable in the cloud on GCP Cloud Run (although you don't have to do the deployment - we will do that ourselves). The scrapers must be horizontally scalable and leverage only selenium in headless mode to ensure they are not incompatible with deployment on Cloud Run.
- The scrapers must save structured data in MongoDB Atlas, using the mongoengine ORM to interface with MongoDB. We have a specific mongoengine model that we will share that we need data stored in. Adding fields to that model as necessary to capture new fields not yet captured is expected.
- Every single field available must be scraped from every patent data source. A meaningful part of this project is investigating the data sources to identify all the data fields available.
- Scraping logic must be robust to variances within the target websites' HTML page structures without using generic try/except statements.
- The scraper must check for a potentially equivalent document already in MongoDB. Using a few different fields (not just a single unique id field), will be necessary to ensure robustness of idempotence for cases where one unique id might be missing from a record.
- We need the fields that are made available by each data source saved on a data-source specific dataclass Python model (i.e. WipoPatent). The scraper class would create instances of the dataclass, and then have a utility for writing the data contained by the dataclass to MongoDB using the generalized mongoengine MongoPatent model we have (as mentioned above).
