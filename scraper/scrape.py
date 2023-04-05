from scraper import beginScraper
from syncKendra import syncKendra
import os
from dotenv import load_dotenv
from uploadS3 import uploadS3

load_dotenv()
bucket_name = os.getenv("S3_BUCKET_NAME")
kendra_data_source_id = os.getenv("KENDRA_DATA_SOURCE_ID")
kendra_index_id = os.getenv("KENDRA_INDEX_ID")
profile_name = os.getenv("PROFILE_NAME")

def scrapeNewData():
    beginScraper(bucket_name,profile_name)
    syncKendra(kendra_data_source_id,kendra_index_id)

def uploadScrapedData():
    uploadS3(bucket_name,profile_name)
    
    
uploadScrapedData()