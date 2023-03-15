from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/page1")
def page1():
    return render_template("page1.html")
@app.route("/page2")
def page2():
    return render_template("page2.html")

# Set up authentication using the JSON client file
creds = service_account.Credentials.from_service_account_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

# Define a route for the GET request
@app.route('/google-sheet-content', methods=['GET'])
def get_google_sheet_content():
    # Define the spreadsheet ID and range
    spreadsheet_id = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
    range_name = 'Sheet1!A1:B2'  # Replace with the range you want to download

    # Fetch the data from the Google Sheets API
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    # Convert the data to JSON and return it
    if not values:
        return jsonify({'error': 'No data found'})
    else:
        return jsonify({'data': values})

if __name__ == "__main__":
    app.run()
