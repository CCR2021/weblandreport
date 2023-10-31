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
        try:
            response_data = response.json()
            if isinstance(response_data, dict):
                return response_data
            else:
                return {"error": "Unexpected response format"}
        except Exception as e:
            return {"error": str(e)}
    return {"error": f"Response status code: {response.status_code}"}

def process_application_data(application_type, dist_codes, appl_no, result_dfs):
    dist_name, mand_name, data_fields = "No Data", "No Data", {}
    final_status = "No Data"

    response_data = get_data_for_district_code(appl_no, application_type['status'], 11)  # First, check district code 11

    if 'Data' in response_data and not response_data.get("error"):
        data = response_data['Data'][0]
        dist_name = data.get('dist_name', "No Data")
        mand_name = data.get('mand_name', "No Data")
        data_fields = {field: data.get(field, None) for field in application_type['fields']}
        final_status = "Found Data"

    for dist_code in dist_codes:
        if final_status == "Found Data":
            break  # Data already found, no need to continue
        if dist_code == 11:
            continue  # Skip district 11 as we already checked it

        response_data = get_data_for_district_code(appl_no, application_type['status'], dist_code)

        if 'Data' in response_data and not response_data.get("error"):
            data = response_data['Data'][0]
            dist_name = data.get('dist_name', "No Data")
            mand_name = data.get('mand_name', "No Data")
            data_fields = {field: data.get(field, None) for field in application_type['fields']}
            final_status = "Found Data"

    # Create DataFrame for this application type
    df_result = pd.DataFrame({
        'appl_no': [appl_no],
        'dist_name': [dist_name],
        'mand_name': [mand_name],
        **data_fields
    })

    result_dfs[application_type['name']].append(df_result)

    return final_status

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
                    result_dfs = {
                        'MUA': [],
                        'MUT': [],
                        'PPB': []
                    }

                    for index, row in df_appl.iterrows():
                        appl_no = row['appl_no']

                        final_status = "No Data"
                        dist_codes = list(range(1, 11)) + list(range(12, 27))

                        if appl_no.startswith('MUA'):
                            final_status = process_application_data(
                                application_type={
                                    'status': 'MCAPMuDist',
                                    'fields': [
                                        'Status_type', 'Appl_date', 'appl_slno', 'appl_syno', 'Khata_Number',
                                        'status', 'form5generateddate', 'Vro_Date', 'tah_approv_reject_date',
                                        'rdo_entrydate', 'tah_reject_date'
                                    ],
                                    'name': 'MUA'
                                },
                                dist_codes=dist_codes,
                                appl_no=appl_no,
                                result_dfs=result_dfs
                            )
                        elif appl_no.startswith('MUT'):
                            final_status = process_application_data(
                                application_type={
                                    'status': 'MCAPMTDist',
                                    'fields': [
                                        'Status_type', 'Appl_date', 'appl_slno', 'appl_syno', 'Khata_Number',
                                        'status', 'form5generateddate', 'Vro_Date', 'tah_approv_reject_date',
                                        'rdo_entrydate', 'tah_reject_date', 'mut_approv_date'
                                    ],
                                    'name': 'MUT'
                                },
                                dist_codes=dist_codes,
                                appl_no=appl_no,
                                result_dfs=result_dfs
                            )

                            process_application_data(
                                application_type={
                                    'status': 'PPbStatus',
                                    'fields': [
                                        'Appl_date', 'appl_slno', 'Khata_Number', 'PPbAppro_RejectDate', 'status'
                                    ],
                                    'name': 'PPB'
                                },
                                dist_codes=dist_codes,
                                appl_no=appl_no,
                                result_dfs=result_dfs
                            )

                    for app_type in result_dfs:
                        df_result = pd.concat(result_dfs[app_type], ignore_index=True)
                        file_name = f"{app_type}_result_response_data.xlsx"
                        df_result.to_excel(file_name, index=False)

                    return "Results exported to:\n" + ', '.join([f"{app_type} - {app_type}_result_response_data.xlsx" for app_type in result_dfs])
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
