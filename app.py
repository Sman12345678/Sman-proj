import os
import logging
import requests
import subprocess
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Chrome binary path
CHROME_PATH = "/tmp/chrome/chrome"

# Function to download a pre-built Chrome binary
def setup_chrome():
    if not os.path.exists(CHROME_PATH):
        logger.info("Chrome not found. Downloading pre-built Chrome binary...")
        os.makedirs("/tmp/chrome", exist_ok=True)
        
        # Download pre-built Chrome binary
        chrome_url = "https://github.com/scheib/chromium-latest-linux/raw/master/chrome-linux.zip"
        chrome_zip_path = "/tmp/chrome/chrome.zip"
        
        response = requests.get(chrome_url, stream=True)
        with open(chrome_zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info("Chrome downloaded. Extracting...")
        subprocess.run(["unzip", "-o", chrome_zip_path, "-d", "/tmp/chrome"], check=True)
        os.chmod(CHROME_PATH, 0o755)
        logger.info("Chrome setup completed.")

# Endpoint to generate image
@app.route("/create", methods=["GET"])
def create_image():
    # Ensure Chrome is installed
    setup_chrome()
    
    # Get the prompt from the query parameter
    prompt = request.args.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    logger.info(f"Received prompt: {prompt}")
    
    # Configure Selenium WebDriver with Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = CHROME_PATH
    
    # Start ChromeDriver
    service = Service(executable_path="/usr/bin/chromedriver")  # Update if chromedriver is elsewhere
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Navigate to the image generation site
        driver.get("https://bing.com/images/create")  # Replace with actual URL
        
        # Enter the prompt and generate the image
        search_box = driver.find_element(By.ID, "b_searchboxForm")
        input_box = search_box.find_element(By.CLASS_NAME, "q")
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)
        
        # Wait for the image to load
        driver.implicitly_wait(10)
        image = driver.find_element(By.CLASS_NAME, "image_row_img.bceimg.mimg")
        image_url = image.get_attribute("src")
        
        logger.info(f"Generated image URL: {image_url}")
        return jsonify({"image_url": image_url})
    
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Use the PORT environment variable in Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
