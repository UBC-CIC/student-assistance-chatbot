from scraper import beginScraper
from syncKendra import syncKendra
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path("../.env"))
bucket_name = os.getenv("S3_BUCKET_NAME")
kendra_data_source_id = os.getenv("KENDRA_DATA_SOURCE_ID")
kendra_index_id = os.getenv("KENDRA_INDEX_ID")
profile_name = os.getenv("PROFILE_NAME")

#beginScraper(bucket_name,profile_name)
syncKendra(kendra_data_source_id,kendra_index_id,profile_name)