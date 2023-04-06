import os
import pathlib
from flask import Flask, abort, redirect, request, render_template, jsonify, session
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol
import json
import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests

app = Flask(__name__)
cors = CORS(app)


# Set up authentication using the JSON client file
creds = service_account.Credentials.from_service_account_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
# Define the spreadsheet ID and range
SPREADSHEET_ID = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
RANGE_NAME = 'General!A2:ZZ'  # Include all columns and rows

# Fetch the data from the Google Sheets API
service = build('sheets', 'v4', credentials=creds)
result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])\

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

# Check if data was retrieved successfully
@app.route('/verify-spreadsheet-access', methods=['GET'])
def verify_spreadsheet_access():
    try:
        # Call the spreadsheets().get() method to check if the API has access to the spreadsheet
        service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        return 'Access to spreadsheet granted!'
    except Exception as e:
        return f'Error: {str(e)}'



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
    print(values[row_index][0])
    
    # Define the spreadsheet ID and range
    SPREADSHEET_ID = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
    RANGE_NAME = values[row_index][0] + '!A2:ZZ'  # Include all columns and rows

    # Fetch the data from the Google Sheets API
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    new_values = result.get('values', [])\
    
    # print(new_values)
    seen_strings = {}
    new_list = []

    for item in new_values:
        if item[0] not in seen_strings:
            seen_strings[item[0]] = True
            new_list.append(item)

    # Render the data_cell.html template with the row data as a context variable
    rendered_data_cell = render_template('data_cell.html', data=new_list)

    # Render the program.html template with the rendered data_cell.html as a context variable
    return render_template('program.html', data=new_list, rendered_data_cell=rendered_data_cell)

#TODO 
@app.route('/render_sub_data_cell/<int:row_index>', methods=['POST'])
def render_sub_data_cell(row_index):
    print(values[row_index][0])
    
    # Define the spreadsheet ID and range
    SPREADSHEET_ID = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
    RANGE_NAME = values[row_index][0] + '!A2:ZZ'  # Include all columns and rows

    # Fetch the data from the Google Sheets API
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    new_values = result.get('values', [])\
    
    # print(new_values)

    # Render the data_cell.html template with the row data as a context variable
    rendered_data_cell = render_template('sub_data_cell.html', data=new_values)

    # Render the program.html template with the rendered sub_data_cell.html as a context variable
    return render_template('module.html', data=new_values, rendered_data_cell=rendered_data_cell)


app.secret_key = "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" # make sure this matches with that's in client_secret.json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

GOOGLE_CLIENT_ID = "930412895866-kl7tqag8khks0bjgknfatq2qldhjuh3g.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret2.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/callback"
)

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    print(authorization_url, state)
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/")

@app.route("/")
def home():
    if 'name' in session:
        print(session['name'] + " est connecté")
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run()
