FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy the contents of fb_profile_scraper into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Start the Cloud Function-compatible HTTP server
# main.py nằm trong core/, nên cần `core.main`
CMD ["gunicorn", "--bind", ":8080", "core.main:crawl_facebook_profiles"]
