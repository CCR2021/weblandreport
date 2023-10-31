from flask import Flask, request, render_template
import pandas as pd
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']

        if uploaded_file.filename != '':
            if uploaded_file.filename.endswith(('.xlsx', '.xls')):
                df_appl = pd.read_excel(uploaded_file)

                if 'appl_no' in df_appl.columns:
                    # Define the base URL
                    base_url = "http://uatwebland.ap.gov.in/WeblandDashboard/WtaxProgress/DS"

                    # Initialize an empty list to store DataFrames for each application number
                    result_dfs = []

                    # Iterate through each row in the DataFrame
                    for index, row in df_appl.iterrows():
                        appl_no = row['appl_no']

                        # Initialize empty lists to store dist_name and mand_name values
                        dist_name_values = []
                        mand_name_values = []

                        # Check if "appl_no" is available for "DistCode: 11"
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
                                dist_name_values.append("No Data")
                                mand_name_values.append("No Data")
                        else:
                            dist_name_values.append("No Data")
                            mand_name_values.append("No Data")
                            print(f"Request for appl_no {appl_no} in DistCode 11 failed with status code {response.status_code}")

                        # If data is not found in DistCode 11, check other DistCodes (1 to 26)
                        if not data_list:
                            for dist_code in range(1, 27):
                                if dist_code == 11:  # Skip district code 11
                                    continue

                                payload = {
                                    "Status": "MCAPMTDist",
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
                                        dist_name_values.append("No Data")
                                        mand_name_values.append("No Data")
                                else:
                                    dist_name_values.append("No Data")
                                    mand_name_values.append("No Data")
                                    print(f"Request for appl_no {appl_no} in DistCode {dist_code} failed with status code {response.status_code}")

                        # Create a new DataFrame for the current application number
                        df_result = pd.DataFrame({'appl_no': [appl_no] * len(dist_name_values), 'dist_name': dist_name_values, 'mand_name': mand_name_values})

                        # Append the DataFrame to the list
                        result_dfs.append(df_result)

                    # Concatenate all DataFrames vertically
                    result_df = pd.concat(result_dfs, ignore_index=True)

                    # Export the result DataFrame to a new Excel file
                    result_excel_file = "result_response_data.xlsx"
                    result_df.to_excel(result_excel_file, index=False)

                    return "Result exported to " + result_excel_file
                else:
                    return "The 'appl_no' column is not present in the uploaded Excel file."
            else:
                return "Please upload a valid Excel file with .xlsx or .xls extension."
        else:
            return "No file uploaded."
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
