import requests
import json
import pandas as pd

# Define the URL dynamically
url = "http://uatwebland.ap.gov.in/WeblandDashboard/WtaxProgress/DS"

# Define the request method (e.g., POST, GET, PUT, DELETE)
request_method = "POST"

# Define the request headers
headers = {
    "Content-Type": "application/json; charset=utf-8",
}

# Define the request payload (data) dynamically
payload = {
    "application_id": "MUA230921037469",  # Replace with your actual application ID
    # Add other payload data as needed
}

# Convert payload to JSON format
payload_json = json.dumps(payload)

# Make the HTTP request
response = requests.request(request_method, url, data=payload_json, headers=headers)

# Define default values for missing data
default_values = {
    "field1": "Default1",
    "field2": "Default2",
    "field3": "Default3",
    # Add more default values as needed
}

# Check the response status code
if response.status_code == 200:
    # If the status code is 200, the request was successful
    print("Request was successful!")

    try:
        # Attempt to parse the response as JSON
        response_data = response.json()

        # Check if 'data' key exists in the response
        if 'data' in response_data:
            data = response_data['data']

            # Fill in missing data with default values
            for key, value in default_values.items():
                if key not in data:
                    data[key] = value

            # Create a DataFrame from the entire 'data' dictionary
            df = pd.DataFrame([data])  # Wrapping 'data' in a list to create a DataFrame
            print("DataFrame created successfully.")
        else:
            print("No 'data' key found in the response JSON.")

    except json.JSONDecodeError:
        # If parsing JSON fails, print the response content as is
        print("Response Content:")
        print(response.text)

else:
    # If the status code is not 200, there was an error
    print(f"Request failed with status code {response.status_code}")
    print("Response Content:")
    print(response.text)  # Print the response content for error debugging
