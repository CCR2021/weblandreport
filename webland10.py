from flask import Flask, request, render_template
import pandas as pd
import requests

app = Flask(__name__)

def get_data_for_district_code(appl_no, status, dist_code):
    base_url = "http://uatwebland.ap.gov.in/WeblandDashboard/WtaxProgress/DS"
    payload = {
        "Status": status,
        "DistCode": dist_code,
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
            return dist_name, mand_name
    return "No Data", "No Data"

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
                    existing_result_dfs = []
                    new_result_dfs = []

                    for index, row in df_appl.iterrows():
                        appl_no = row['appl_no']

                        # Initialize data for both existing and new requests
                        existing_dist_name = "No Data"
                        existing_mand_name = "No Data"
                        new_dist_name = "No Data"
                        new_mand_name = "No Data"

                        # Check the application number for DistCode=11 for existing request
                        existing_dist_name, existing_mand_name = get_data_for_district_code(appl_no, "MCAPMuDist", "11")

                        # If not found in DistCode=11, check other DistCodes (1-10, 12-26) for existing request
                        if existing_dist_name == "No Data":
                            for dist_code in range(1, 11):
                                existing_dist_name, existing_mand_name = get_data_for_district_code(appl_no, "MCAPMTDist", str(dist_code))
                                if existing_dist_name != "No Data":
                                    break  # Exit loop if data is found
                            if existing_dist_name == "No Data":
                                for dist_code in range(12, 27):
                                    existing_dist_name, existing_mand_name = get_data_for_district_code(appl_no, "MCAPMTDist", str(dist_code))
                                    if existing_dist_name != "No Data":
                                        break  # Exit loop if data is found

                        # Check the application number for DistCode=11 for new request
                        new_dist_name, new_mand_name = get_data_for_district_code(appl_no, "PPbStatus", "11")

                        # If not found in DistCode=11, check other DistCodes (1-10, 12-26) for new request
                        if new_dist_name == "No Data":
                            for dist_code in range(1, 11):
                                new_dist_name, new_mand_name = get_data_for_district_code(appl_no, "PPbStatus", str(dist_code))
                                if new_dist_name != "No Data":
                                    break  # Exit loop if data is found
                            if new_dist_name == "No Data":
                                for dist_code in range(12, 27):
                                    new_dist_name, new_mand_name = get_data_for_district_code(appl_no, "PPbStatus", str(dist_code))
                                    if new_dist_name != "No Data":
                                        break  # Exit loop if data is found

                        # Create DataFrames for existing and new requests
                        existing_df_result = pd.DataFrame({'appl_no': [appl_no], 'dist_name': [existing_dist_name], 'mand_name': [existing_mand_name]})
                        new_df_result = pd.DataFrame({'appl_no': [appl_no], 'dist_name': [new_dist_name], 'mand_name': [new_mand_name]})

                        existing_result_dfs.append(existing_df_result)
                        new_result_dfs.append(new_df_result)

                    existing_result_df = pd.concat(existing_result_dfs, ignore_index=True)
                    new_result_df = pd.concat(new_result_dfs, ignore_index=True)

                    existing_result_excel_file = "existing_result_response_data.xlsx"
                    new_result_excel_file = "new_result_response_data.xlsx"

                    existing_result_df.to_excel(existing_result_excel_file, index=False)
                    new_result_df.to_excel(new_result_excel_file, index=False)

                    return "Result exported to:\nExisting Request - " + existing_result_excel_file + "\nNew Request - " + new_result_excel_file
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
