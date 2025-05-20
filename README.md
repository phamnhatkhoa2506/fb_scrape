gcloud builds submit --tag gcr.io/creator-dev-453406/fb_profile_scraper

gcloud run deploy fb_profile_scraper --image gcr.io/creator-dev-453406/fb_profile_scraper --region=asia-southeast1 --platform=managed --allow-unauthenticated --service-account=export-social-data@creator-dev-453406.iam.gserviceaccount.com --env-vars-file ../env.json

* Deploy
gcloud functions deploy crawl_facebook_profiles --runtime python312 --trigger-http --entry-point crawl_facebook_profiles --region asia-southeast1 --memory 5000MB --timeout 1000s --service-account export-social-data@creator-dev-453406.iam.gserviceaccount.com --env-vars-file ../env.json

́* Cấp quyền 
gcloud iam service-accounts add-iam-policy-binding export-social-data@creator-dev-453406.iam.gserviceaccount.com --member="user:khoaphamnhat2506@gmail.com" --role="roles/iam.serviceAccountUser"
