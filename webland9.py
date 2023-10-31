from flask import Flask, request, render_template
import pandas as pd
import requests
from itertools import chain

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

                    for index, row in df_appl.iterrows():
                        appl_no = row['appl_no']

                        dist_name = "No Data"  # Initialize with "No Data"
                        mand_name = "No Data"  # Initialize with "No Data"

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

                        # If not found in DistCode 11, check other DistCodes (1-10, 12-26)
                        if dist_name == "No Data":
                            for dist_code in chain(range(1, 11), range(12, 27)):  # Concatenate two ranges
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
                                        break  # Exit the loop as the application is found

                        # Create a new DataFrame for the current application number
                        df_result = pd.DataFrame({'appl_no': [appl_no], 'dist_name': [dist_name], 'mand_name': [mand_name]})

                        # Append the DataFrame to the list
                        result_dfs.append(df_result)

                    result_df = pd.concat(result_dfs, ignore_index=True)

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
