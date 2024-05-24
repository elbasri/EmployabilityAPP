from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.job_spider import JobSpider
from ml_model.predictor import EmploymentPredictor
from config import Config
import os

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

    # Initialize the predictor
    predictor = EmploymentPredictor()
    
    # Load the existing model if it exists
    model_path = Config.base_Path + 'ml_model/trained/model.joblib'
    if os.path.exists(model_path):
        predictor.load_model(model_path)
        print("Existing model loaded.")
    else:
        print("No existing model found. Training a new model.")

    # Run the full pipeline: data extraction, preprocessing, training, and evaluation
    predictor.full_pipeline()

    # Save the updated or new model
    predictor.save_model(model_path)
    print("Model training complete and saved.")

    if predictor.model is not None:
        predictor.evaluate_model()
    else:
        print("Model not trained or loaded.")

if __name__ == '__main__':
    run_spiders()
