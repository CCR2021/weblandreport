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
            dist_name = data.get('dist_name', "No Data")
            mand_name = data.get('mand_name', "No Data")
            return data, dist_name, mand_name
    return {}, "No Data", "No Data"

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
                        data, existing_dist_name, existing_mand_name = get_data_for_district_code(appl_no, "MCAPMuDist", "11")
                        new_data, new_dist_name, new_mand_name = get_data_for_district_code(appl_no, "PPbStatus", "11")

                        # If not found in DistCode=11, check other DistCodes (1-10, 12-26) for existing request
                        if existing_dist_name == "No Data":
                            for dist_code in range(1, 11):
                                data, existing_dist_name, existing_mand_name = get_data_for_district_code(appl_no, "MCAPMTDist", str(dist_code))
                                if existing_dist_name != "No Data":
                                    break  # Exit loop if data is found
                            if existing_dist_name == "No Data":
                                for dist_code in range(12, 27):
                                    data, existing_dist_name, existing_mand_name = get_data_for_district_code(appl_no, "MCAPMTDist", str(dist_code))
                                    if existing_dist_name != "No Data":
                                        break  # Exit loop if data is found

                        # If not found in DistCode=11, check other DistCodes (1-10, 12-26) for new request
                        if new_dist_name == "No Data":
                            for dist_code in range(1, 11):
                                new_data, new_dist_name, new_mand_name = get_data_for_district_code(appl_no, "PPbStatus", str(dist_code))
                                if new_dist_name != "No Data":
                                    break  # Exit loop if data is found
                            if new_dist_name == "No Data":
                                for dist_code in range(12, 27):
                                    new_data, new_dist_name, new_mand_name = get_data_for_district_code(appl_no, "PPbStatus", str(dist_code))
                                    if new_dist_name != "No Data":
                                        break  # Exit loop if data is found

                        # Initialize variables for data fields
                        existing_vill_name = existing_status_type = existing_appl_date = existing_appl_slno = existing_appl_syno = existing_khata_number = existing_status = existing_form5generateddate = existing_vro_date = existing_tah_approv_reject_date = existing_rdo_entrydate = existing_tah_reject_date = existing_mut_approv_date = None
                        new_vill_name = new_appl_date = new_appl_slno = new_khata_number = new_ppb_appro_reject_date = new_status = None

                        # Retrieve data fields for existing request
                        if isinstance(data, dict):
                            existing_vill_name = data.get('vill_name', None)
                            existing_status_type = data.get('Status_type', None)
                            existing_appl_date = data.get('Appl_date', None)
                            existing_appl_slno = data.get('appl_slno', None)
                            existing_appl_syno = data.get('appl_syno', None)
                            existing_khata_number = data.get('Khata_Number', None)
                            existing_status = data.get('status', None)
                            existing_form5generateddate = data.get('form5generateddate', None)
                            existing_vro_date = data.get('Vro_Date', None)
                            existing_tah_approv_reject_date = data.get('tah_approv_reject_date', None)
                            existing_rdo_entrydate = data.get('rdo_entrydate', None)
                            existing_tah_reject_date = data.get('tah_reject_date', None)
                            existing_mut_approv_date = data.get('mut_approv_date', None)

                        # Retrieve data fields for new request
                        if isinstance(new_data, dict):
                            new_vill_name = new_data.get('vill_name', None)
                            new_appl_date = new_data.get('Appl_date', None)
                            new_appl_slno = new_data.get('appl_slno', None)
                            new_khata_number = new_data.get('Khata_Number', None)
                            new_ppb_appro_reject_date = new_data.get('PPbAppro_RejectDate', None)
                            new_status = new_data.get('status', None)

                        # Create DataFrames for existing and new requests
                        existing_df_result = pd.DataFrame({
                            'appl_no': [appl_no],
                            'dist_name': [existing_dist_name],
                            'mand_name': [existing_mand_name],
                            'vill_name': [existing_vill_name],
                            'Status-type': [existing_status_type],
                            'Appl_date': [existing_appl_date],
                            'appl_slno': [existing_appl_slno],
                            'appl_syno': [existing_appl_syno],
                            'khata_Number': [existing_khata_number],
                            'status': [existing_status],
                            'form5generateddate': [existing_form5generateddate],
                            'vro_Date': [existing_vro_date],
                            'tah_approv_reject_date': [existing_tah_approv_reject_date],
                            'rdo_entrydate': [existing_rdo_entrydate],
                            'tah_reject_date': [existing_tah_reject_date],
                            'mut_approv_date': [existing_mut_approv_date]
                        })

                        new_df_result = pd.DataFrame({
                            'appl_no': [appl_no],
                            'dist_name': [new_dist_name],
                            'mand_name': [new_mand_name],
                            'vill_name': [new_vill_name],
                            'Appl_date': [new_appl_date],
                            'appl_slno': [new_appl_slno],
                            'khata_Number': [new_khata_number],
                            'PPbAppro_RejectDate': [new_ppb_appro_reject_date],
                            'status': [new_status]
                        })

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
