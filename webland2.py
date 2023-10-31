import requests
import pandas as pd

# Define the base URL
base_url = "http://uatwebland.ap.gov.in/WeblandDashboard/WtaxProgress/DS"

# Define the payload data for the POST request
payload = {
    "Status": "MCAPMuDist",
    "DistCode": "24",
    "appl_no": "MUT221202036690"
}

# Make the POST request
response = requests.post(base_url, json=payload)

# Check the response status code
if response.status_code == 200:
    # If the status code is 200, the request was successful
    print("Request was successful!")

    # Parse the JSON response into a DataFrame
    response_data = response.json()
    df = pd.DataFrame(response_data)

    # Export the DataFrame to an Excel file
    excel_file = "response_data.xlsx"
    df.to_excel(excel_file, index=False)

    print(f"Data exported to {excel_file}")
else:
    # If the status code is not 200, there was an error
    print(f"Request failed with status code {response.status_code}")
    print("Response Content:")
    print(response.text)  # Print the response content for error debugging
