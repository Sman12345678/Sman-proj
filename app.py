from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)

@app.route('/create', methods=['GET'])
def create_image():
    # Get the prompt from the query parameter
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser window)
    driver = webdriver.Chrome(options=options)

    try:
        # Open the target website
        driver.get("https://example.com")

        # Find the type container (input field) and enter the prompt
        input_box = driver.find_element(By.ID, "b_searchbox gi_sb")
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(5)

        # Find the image container and extract the image URL
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
