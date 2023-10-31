import requests
import pandas as pd

# Define the base URL
base_url = "http://uatwebland.ap.gov.in/WeblandDashboard/WtaxProgress/DS"

# Define the payload data for the POST request
payload = {
    "Status": "MCAPMuDist",
    "DistCode": "11",
    "appl_no": "MUT230905052895"
}

# Make the POST request
response = requests.post(base_url, json=payload)

# Check the response status code
if response.status_code == 200:
    # If the status code is 200, the request was successful
    print("Request was successful!")

    # Parse the JSON response into a DataFrame
    response_data = response.json()

    # Access 'dist_name' and 'mand_name' from the 'Data' list
    data_list = response_data.get('Data', [])
    if data_list:
        data = data_list[0]  # Assuming there's only one item in the list

        # Create a DataFrame with columns 'dist_name' and 'mand_name'
        df = pd.DataFrame(columns=['dist_name', 'mand_name'])

        # Extract 'dist_name' and 'mand_name' from the 'data' dictionary
        dist_name = data.get('dist_name', '')
        mand_name = data.get('mand_name', '')

        new_data = {'dist_name': [dist_name], 'mand_name': [mand_name]}
        df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)

        # Export the DataFrame to a new Excel file
        excel_file = "new_response_data.xlsx"
        df.to_excel(excel_file, index=False)

        print(f"Data appended to {excel_file}")
    else:
        print("No data found in the 'Data' list.")
else:
    # If the status code is not 200, there was an error
    print(f"Request failed with status code {response.status_code}")
    print("Response Content:")
    print(response.text)  # Print the response content for error debugging
