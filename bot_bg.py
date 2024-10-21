from flask import Flask, render_template, request, jsonify
import requests
import logging
import urllib.parse

app = Flask(__name__)

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('ind.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Extract JSON data from the request
    data = request.json
    message = data.get('message')

    # Log the received message for debugging purposes
    app.logger.debug(f"Received message: {message}")

    if not message:
        app.logger.error("No message provided in the request.")
        return jsonify({'error': 'No message provided'})

    try:
        # Encode the message to be URL-safe
        encoded_message = urllib.parse.quote(message)
        app.logger.debug(f"Encoded message: {encoded_message}")

        # Construct the API URL (using subhatde API)
        api_base_url = "https://subhatde.id.vn/sim?type=ask&ask="
        api_url = f"{api_base_url}{encoded_message}"
        app.logger.debug(f"API URL: {api_url}")

        # Make a GET request to the external API with a timeout of 10 seconds
        response = requests.get(api_url, timeout=10)
        app.logger.debug(f"API Response Status Code: {response.status_code}")
        app.logger.debug(f"API Response Text: {response.text}")

        # If the API call is successful, parse the response
        if response.status_code == 200:
            try:
                response_data = response.json()
                app.logger.debug(f"API JSON Response: {response_data}")
                # Extracting the "answer" field from the JSON response
                return jsonify({'reply': response_data.get('answer', 'Không có câu trả lời')})
            except ValueError:
                app.logger.error("Failed to decode JSON from API response.")
                return jsonify({'error': 'Invalid response from API.'})
        else:
            app.logger.error(f"API returned an error: {response.status_code}")
            return jsonify({'error': f'API error: {response.status_code}'})

    except requests.exceptions.Timeout:
        app.logger.error("API request timed out.")
        return jsonify({'error': 'Request timed out. Please try again.'})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return jsonify({'error': 'Error connecting to the API.'})

if __name__ == '__main__':
    app.run(debug=True)
