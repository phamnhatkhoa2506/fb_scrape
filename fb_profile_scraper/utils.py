import json
import pytz
import traceback
from typing import List, Dict, Generator
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from apify_client import ApifyClient
from google.cloud import storage

from core.api_keys import API_KEYS
from core.key_manager import APIKeyManager


# Constants
BUCKET_PROFILE_NAME = "influencer-profile"
MAX_ITEMS = 10


def convert_urls(urls: List[str]) -> List[dict[str, str]]:
    '''
        Convert list of url string into apify list of url form

        Params:
            urls(List[str]): List of url string

        Return:
            List of APIFY-formalized urls
    '''

    url_dicts = [{"url": url} for url in urls]
    return url_dicts


def batch(url_list: List[Dict[str, str]], batch_size: int) -> Generator[List[Dict[str, str]], None, None]:
    '''
        Create batches from the list of urls with a size of batch

        Params:
            url_list (List): List of urls
            batch_size (int): size of the batch

        Return:
            Iterator of the batches
    '''

    for i in range(0, len(url_list), batch_size):
        yield url_list[i:i + batch_size]


def process_batch(batch: List[Dict[str, str]], key_manager: APIKeyManager) -> List[Dict]:
    '''
        Process the input batch for each API KEYS to ensure that they work.
        If they dont't work, return empty list.

        Params:
            batch (List): list of the input urls
            key_manager (APIKeyManager): the manager to switch keys

        Return:
            The list of data after being scraped
    '''

    run_input = {"startUrls": batch} # APIFY input form

    for _ in range(len(API_KEYS)):
        api_key = key_manager.get() # Get apikey
        print(f"[Batch {batch}] Use API key: {api_key}")

        try:
            # Create client
            client = ApifyClient(api_key)
            run = client.actor("4Hv5RhChiaDk6iwad").call(run_input=run_input)

            # Run the actor
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise Exception("dataset ID not found")

            # Get ites
            items = list(client.dataset(dataset_id).iterate_items())
    
            # Keep the order of the batches
            items = sorted(items, key=lambda item: batch.index(item["url"]) if "url" in item else len(batch))

            print(f"[Batch {batch}] Run completely {len(items)} user")

            return items

        except Exception as e:
            print(f"[Batch {batch}] Failed key {api_key}: {e}")
            traceback.print_exc()
            key_manager.switch()

    print(f"[Batch {batch}] All keys can not be used.")

    return []


def scrape_profiles_from_urls(urls: List[Dict[str, str]], batch_size: int = 2) -> List[Dict]:
    '''
        Split the url list into batches, process each batch and synthezie all result from batches.

        Params:
            urls (List): list of the urls with apify form
            batch_size (int): size of the batch

        Return:
            List of the all profile data
    '''

    batches = list(batch(urls, batch_size=batch_size)) # Split into batch

    key_managers = [APIKeyManager([API_KEYS[i % len(API_KEYS)]]) for i in range(len(batches))] # Create key manager

    results_dict = {} 

    # Run multithreading task
    with ThreadPoolExecutor(max_workers=min(len(API_KEYS), len(batches))) as executor:
        future_to_index = {
            executor.submit(process_batch, batch, key_managers[i]): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                items = future.result()
                results_dict[i] = items
            except Exception as exc:
                print(f"[Batch {i}] Unexpected error: {exc}")
                traceback.print_exc()

    # Synthesize all data
    all_items = []
    for i in sorted(results_dict.keys()):
        all_items.extend(results_dict[i])

    return all_items


def upload_json_to_gcs(data: List[Dict]) -> str:
    """
        Upload the result to google cloud service

        params:
            data (List[Dict]): list of scraped profiles

        Return:
            gs string
    """

    client = storage.Client()  # create Client
    bucket = client.bucket(BUCKET_PROFILE_NAME) 

    # Get the time
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = int(now.timestamp())

    # Get the destination path
    destination_blob_path = f"facebook/year={year}/month={month}/day={day}/facebook_profile_{timestamp}.json"
    blob = bucket.blob(destination_blob_path) # define destination file

    # Convert data to json string
    json_str = json.dumps(data, ensure_ascii=False, indent=4) # json string 
    blob.upload_from_string(json_str, content_type="application/json")  # upload file

    print(f"Upload JSON data to gs://{BUCKET_PROFILE_NAME}/{destination_blob_path} completely.")

    return f"gs://{BUCKET_PROFILE_NAME}/{destination_blob_path}"