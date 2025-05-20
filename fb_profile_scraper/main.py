import traceback
from flask import Flask, request, jsonify
from utils import (
    convert_urls,
    scrape_profiles_from_urls,
    upload_json_to_gcs
)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def crawl_facebook_profiles():
    """
        Cloud Run HTTP entry point to crawl Facebook profiles.
    """
    try:
        request_json = request.get_json(silent=True)

        if not request_json or "urls" not in request_json:
            return jsonify(error="Key 'urls' not in the request body"), 400

        urls = request_json["urls"]
        if not isinstance(urls, list) or not all(isinstance(u, str) for u in urls):
            return jsonify(error="'urls' must be a list of strings"), 400

        try:
            batch_size = int(request_json.get("batch_size", 2))
        except ValueError:
            return jsonify(error="'batch_size' must be an integer"), 400

        print(f"Starting to scrape {len(urls)} user(s), batch size: {batch_size}")

        urls = convert_urls(urls)
        data = scrape_profiles_from_urls(urls, batch_size)
        gcs_path = upload_json_to_gcs("influencer-profile", data)

        msg = f"Finished. Upload JSON to: {gcs_path}"
        print(msg)

        return jsonify(message=msg), 200

    except Exception as e:
        err_msg = f"Error: {str(e)}"
        print(err_msg)
        traceback.print_exc()
        return jsonify(error=err_msg), 500
