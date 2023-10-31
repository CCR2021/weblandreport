# ...

# Iterate through each row in the DataFrame
for index, row in df_appl.iterrows():
    appl_no = row['appl_no']

    # Initialize empty lists to store dist_name and mand_name values
    dist_name_values = []
    mand_name_values = []

    # First, check if "appl_no" is available for "DistCode: 11"
    payload = {
        "Status": "MCAPMuDist",
        "DistCode": "11",
        "appl_no": appl_no
    }

    response = requests.post(base_url, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        data_list = response_data.get('Data', [])
        if data_list:
            data = data_list[0]
            dist_name = data.get('dist_name', '')
            mand_name = data.get('mand_name', '')
            dist_name_values.append(dist_name)
            mand_name_values.append(mand_name)
        else:
            # If not found in DistCode 11, check other DistCodes (1 to 26)
            for dist_code in range(1, 27):
                payload = {
                    "Status": "MCAPMuDist",
                    "DistCode": str(dist_code),
                    "appl_no": appl_no
                }

                response = requests.post(base_url, json=payload)

                if response.status_code == 200:
                    response_data = response.json()
                    data_list = response_data.get('Data', [])
                    if data_list:
                        data = data_list[0]
                        dist_name = data.get('dist_name', '')
                        mand_name = data.get('mand_name', '')
                        dist_name_values.append(dist_name)
                        mand_name_values.append(mand_name)
                    else:
                        # Append None or an empty string for no data
                        dist_name_values.append(None)
                        mand_name_values.append(None)
                        print(f"No data found for appl_no {appl_no} in DistCode {dist_code}.")
                else:
                    print(f"Request for appl_no {appl_no} in DistCode {dist_code} failed with status code {response.status_code}")

    else:
        print(f"Request for appl_no {appl_no} in DistCode 11 failed with status code {response.status_code}")

    # Create a new DataFrame for the current application number
    df_result = pd.DataFrame({'appl_no': [appl_no], 'dist_name': dist_name_values, 'mand_name': mand_name_values})

    # Append the DataFrame to the list
    result_dfs.append(df_result)

# ...
