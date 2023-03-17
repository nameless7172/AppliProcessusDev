from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

app = Flask(__name__)
cors = CORS(app)


# Set up authentication using the JSON client file
creds = service_account.Credentials.from_service_account_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
# Define the spreadsheet ID and range
SPREADSHEET_ID = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
RANGE_NAME = 'Programme 1!A1:ZZ'  # Include all columns and rows

# Fetch the data from the Google Sheets API
service = build('sheets', 'v4', credentials=creds)
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])\

# Check if data was retrieved successfully
@app.route('/verify-spreadsheet-access', methods=['GET'])
def verify_spreadsheet_access():
    try:
        # Call the spreadsheets().get() method to check if the API has access to the spreadsheet
        service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        return 'Access to spreadsheet granted!'
    except Exception as e:
        return f'Error: {str(e)}'


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/programmes")
def programmes():
    return render_template("programmes.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/google-sheet-content', methods=['GET'])
def get_google_sheet_content():
    # Check if data was retrieved successfully
    if not values:
        return jsonify({'error': 'No data found'})

    # Render the template with the data as a context variable
    return render_template('datatable.html', data=values)

@app.route('/render_data_cell/<int:row_index>', methods=['POST'])
def render_data_cell(row_index):
    # Get the row of data corresponding to the clicked element
    row_data = values[row_index]

    # Render the data_cell.html template with the row data as a context variable
    rendered_data_cell = render_template('data_cell.html', data=row_data)

    # Render the program.html template with the rendered data_cell.html as a context variable
    return render_template('program.html', data=row_data, rendered_data_cell=rendered_data_cell)




if __name__ == "__main__":
    app.run()
