from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.job_spider import JobSpider
from ml_model.predictor import EmploymentPredictor
from config import Config
import os

def train_model():
    predictor = EmploymentPredictor()

    model_path = 'ml_model/trained/model.h5'
    #if os.path.exists(model_path):
    #    predictor.load_model(model_path)
    #    print("Existing model loaded.")
    #else:
    #    print("No existing model found. Training a new model.")

    predictor.full_pipeline()

    if predictor.model:
        predictor.evaluate_model()
    else:
        print("Model not trained or loaded.")

def run_spiders():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.DATABASE_NAME]
    collection = db[Config.URLS_COLLECTION]
    urls = collection.find({}, {'_id': 0, 'url': 1})
    
    # Ensure there are URLs to crawl
    url_list = [url_doc['url'] for url_doc in urls]
    if not url_list:
        print("No URLs found to crawl.")
        return

    process = CrawlerProcess(get_project_settings())
    
    for url in url_list:
        process.crawl(JobSpider, url=url)
    
    process.start()  # the script will block here until all crawling jobs are finished

    train_model()

if __name__ == '__main__':
    run_spiders()
