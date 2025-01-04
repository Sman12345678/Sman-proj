from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import time

app = Flask(__name__)

@app.route('/create', methods=['GET'])
def create_image():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Automatically install the correct version of ChromeDriver
    chromedriver_autoinstaller.install()

    # Set up Selenium WebDriver with headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/usr/bin/google-chrome'  # Path to Chrome on Render

    driver = webdriver.Chrome(options=options)

    try:
        # Open the target website
        driver.get("https://bing.com/images/create")  # Replace with the actual URL

        # Locate the input box and submit the prompt
        input_box = driver.find_element(By.ID, "b_searchbox gi_sb")
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)

        # Wait for the image to load
        time.sleep(8)

        # Extract the image URL
        img_container = driver.find_element(By.CLASS_NAME, "imgri-container")
        img_tag = img_container.find_element(By.CLASS_NAME, "image_row_img")
        img_url = img_tag.get_attribute("src")

        return jsonify({'image_url': img_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=3000)
