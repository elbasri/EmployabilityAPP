import scrapy
from spiders.items import JobItem
from pymongo import MongoClient
from config import Config
import random
import re

class JobSpider(scrapy.Spider):
    name = "job_spider"

    def __init__(self, url=None, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else self.load_start_urls()
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.jobs_collection = self.db[Config.JOBS_COLLECTION]
        self.functions_collection = self.db[Config.functions_collection]
        self.sectors_collection = self.db[Config.sectors_collection]
        self.new_jobs_count = 0

    def load_start_urls(self):
        collection = self.db[Config.URLS_COLLECTION]
        urls = list(collection.find({}, {'_id': 0, 'url': 1}))
        return [url['url'] for url in urls]

    def get_numeric_value(self, collection, value):
        doc = collection.find_one({'name': value})
        if doc:
            return doc['numeric_value']
        else:
            numeric_value = collection.count_documents({}) + 1
            collection.insert_one({'name': value, 'numeric_value': numeric_value})
            return numeric_value

    def parse(self, response):
        for job in response.xpath('//ul[@id="post-data"]/li'):
            job_detail_url = response.urljoin(job.xpath('.//h2/a[@class="titreJob"]/@href').get())
            if not self.jobs_collection.find_one({'job_detail_url': job_detail_url}):
                item = self.extract_job_item(job, response, job_detail_url)
                self.jobs_collection.insert_one(dict(item))
                self.new_jobs_count += 1
                yield item
                non_employable_item = self.create_non_employable_version(item)
                self.jobs_collection.insert_one(non_employable_item)
                yield non_employable_item

    def extract_job_item(self, job, response, job_detail_url):
        item = JobItem()
        item['job_title'] = job.xpath('.//h2/a[@class="titreJob"]/text()').get().strip()
        item['job_detail_url'] = job_detail_url
        item['job_listed'] = job.xpath('.//em[@class="date"]/text()').extract()[1].strip()
        item['company_name'] = job.xpath('.//div[@class="info"]/span/text()').extract_first().strip()
        item['company_link'] = response.urljoin(job.xpath('.//a[@class="photo"]/@href').get())
        item['company_location'] = job.xpath('.//h2/a[contains(@href, "emploi")]/text()').extract_first().split('|')[-1].strip()
        date_section = job.xpath('.//em[@class="date"]/span/text()').extract()
        item['publication_start_date'] = date_section[0].strip()
        item['publication_end_date'] = date_section[1].strip()
        item['post_offered'] = job.xpath('.//em[contains(text(), "Postes proposés:")]/span/text()').get()
        item['sector_activity'] = [s.strip() for s in job.xpath('.//li[contains(text(), "Secteur d\'activité")]/a/text()').getall()]
        item['function'] = [s.strip() for s in job.xpath('.//li[contains(text(), "Fonction")]/a/text()').getall()]
        item['experience_required'] = [self.extract_minimum_experience(s.strip()) for s in job.xpath('.//li[contains(text(), "Expérience requise")]/a/text()').getall()]
        item['study_level_required'] = self.extract_education(job.xpath('.//li[contains(text(), "Niveau d\'étude demandé")]/a/text()').get().strip())
        item['contract_type_offered'] = job.xpath('.//li[contains(text(), "Type de contrat proposé")]/a/text()').get().strip()
        item['Employable'] = 1
        return item

    def extract_minimum_experience(self, exp_string):
        # Extract the numeric value from the experience string
        matches = re.findall(r'\d+', exp_string)
        return [int(num) for num in matches] if matches else [0]

    def extract_education(text):
        """ Map educational levels to structured format. """
        levels = ['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']
        values = [0] * len(levels)
        if 'Bac' in text and 'Bac +' not in text:
            values[0] = 1 
        if 'Bac +2' in text:
            values[0:2] = [1, 1] 
        if 'Bac +3' in text:
            values[0:3] = [1, 1, 1]
        if 'Bac +4' in text:
            values[0:4] = [1, 1, 1, 1] 
        if 'Bac +5' in text or 'Bac +5 et plus' in text:
            values[0:5] = [1, 1, 1, 1, 1] 
        if 'Doctorat' in text or 'Doctorate' in text:
            values[:] = [1, 1, 1, 1, 1, 1]  

        return dict(zip(levels, values))

    def create_non_employable_version(self, item):
        non_item = dict(item)
        non_item['Employable'] = 0

        # Handle experience being a list of integers
        if item['experience_required']:
            # Convert all experiences to integers if possible and reduce randomly
            experiences = [max(0, exp - random.randint(1, 3)) for exp in item['experience_required'][0]]
            non_item['experience_required'] = experiences
        else:
            non_item['experience_required'] = [0]  # Default to zero if no experience is found

        # Downgrade education level
        for level in reversed(['Bac', 'Bac +2', 'Bac +3', 'Bac +4', 'Bac +5', 'Doctorate']):
            if item['study_level_required'].get(level, 0) == 1:
                non_item['study_level_required'][level] = 0
                break  # Only downgrade the first (highest) level found

        return non_item

    def close(self, reason):
        self.client.close()
        if self.new_jobs_count == 0:
            self.logger.info("No new jobs were scraped.")
        else:
            self.logger.info(f"Scraped {self.new_jobs_count} new jobs.")
