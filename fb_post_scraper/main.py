import traceback
from typing import Any

from utils import (
    convert_urls,
    scrape_posts_from_urls,
    upload_json_to_gcs,
)


def crawl_facebook_posts(request: Any) -> Any:
    """
        Cloud Function: Crawl facebook posts
    """

    try:
        # Get urls
        request_json = request.get_json(silent=True)

        if not request_json or "urls" not in request_json:
            return "Key 'urls' not in the request body", 400

        urls = request_json["urls"]
        if not isinstance(urls, list) or not all(isinstance(u, str) for u in urls):
            return "'urls' must be the list of string", 400

        try:
            batch_size = int(request_json.get("batch_size", 2))
        except ValueError:
            return "'batch_size' must be an integer", 400

        print(f"Starting to scrape {len(urls)} user, batch size: {batch_size}")

        urls = convert_urls(urls) # Converst urls to apify form
        data = scrape_posts_from_urls(urls, batch_size) # Run scraping
        gcs_path = upload_json_to_gcs("influencer-profile", data) # Upload to gs

        msg = f"Finished. Upload JSON to: {gcs_path}"
        print(msg)
        
        return msg, 200

    except Exception as e:
        err_msg = f"Error: {str(e)}"
        print(err_msg)
        traceback.print_exc()

        return err_msg, 500
