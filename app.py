import datetime
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
# SPREADSHEET_ID = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
with open('client_secret.json') as f:
    config_data = f.read()
config = json.loads(config_data)

SPREADSHEET_ID = config['SPREADSHEET_ID']
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
        return 'Le fichier de configuration client_secret.json est correcte. Vous avez accès au fichier Google Sheet'
    except Exception as e:
        return f'Error: {str(e)}'



@app.route("/programmes")
def programmes():
    if "logged_in" not in session or not session["logged_in"] or 'name' not in session:
        return redirect("/login")
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
    # SPREADSHEET_ID = '1sokVn-TX3t1DQ3IQPAAl7B-F_xnyZfLYShrJ_MxEfGY'
    RANGE_NAME = values[row_index][0] + '!A2:ZZ'  # Include all columns and rows
    session["programmeNumber"] = row_index
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
    print(new_list)
    # Render the data_cell.html template with the row data as a context variable
    # rendered_data_cell = render_template('data_cell.html', data=new_list)

    # Render the program.html template with the rendered data_cell.html as a context variable
    return render_template('program.html', data=new_list)


@app.route('/render_sub_data_cell/<int:row_index>', methods=['POST'])
def render_sub_data_cell(row_index):
    session["moduleNumber"] = row_index + 1
    # Define the spreadsheet ID and range
    RANGE_NAME = values[session['programmeNumber']][0] + '!A2:ZZ'  # Include all columns and rows

    # Fetch the data from the Google Sheets API
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    new_values = result.get('values', [])\
    
    seen_strings = {}
    new_list = []

    # print(new_values)
    for item in new_values:
        if item[0] not in seen_strings:
            seen_strings[item[0]] = True
            new_list.append(item)
    # print(new_list)

    exercises_by_module = {}
    # Loop through each exercise in the array
    for exercise in new_values:
    # Extract the module and exercise names
        module = exercise[0]
        exercise_name = exercise[1]
        
        # If the module is not already in the dictionary, add it with an empty list
        if module not in exercises_by_module:
            exercises_by_module[module] = []
        
        # Add the exercise to the list for the current module
        exercises_by_module[module].append(exercise_name)

    # Render the program.html template with the rendered sub_data_cell.html as a context variable
    return render_template('module.html', data=exercises_by_module)



@app.route('/render_sub_sub_data_cell/<int:row_index>', methods=['POST'])
def render_sub_sub_data_cell(row_index):
    url = request.url
    
    # Define the spreadsheet ID and range
    RANGE_NAME = values[session['programmeNumber']][0] + '!A2:ZZ'  # Include all columns and rows

    # Fetch the data from the Google Sheets API
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    new_values = result.get('values', [])\
    


    # Render the data_cell.html template with the row data as a context variable
    # rendered_data_cell = render_template('sub_data_cell.html', data=new_values)
    # Render the data_cell.html template
    # Render the program.html template with the rendered sub_data_cell.html as a context variable
    return render_template('exercice.html', data=new_values, url=url)



app.secret_key = "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" # make sure this matches with that's in client_secret.json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

GOOGLE_CLIENT_ID = "930412895866-kl7tqag8khks0bjgknfatq2qldhjuh3g.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret2.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:5000/callback"
)

@app.route("/CommencerExercice", methods=['POST'])
def commencer_exercice():
    data = request.get_json()  # get the data sent in the request
    module_number = data['moduleNumber']
    exercice = data['exercice']
    exercice_number = int(data['exercice'][-1])
    # process the data
    # Define the spreadsheet ID and range
    RANGE_NAME = values[session['programmeNumber']][0] + '!A2:ZZ'  # Include all columns and rows
    # Fetch the data from the Google Sheets API
    creds = service_account.Credentials.from_service_account_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    
    # loop through each row of the sheet data
    for i, row in enumerate(result['values']):
        # check if the second column contains the exercice string and the last character of the first column is the module_number
        today = datetime.date.today().isoformat()
        if row[1] == exercice and row[0][-1] == module_number:
            result['values'][i][7] = today
            result['values'][i][5] = "en cours"

    # update the spreadsheet with the modified data
    body = {
        'values': result['values']
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()

    
    return 'Data received',200


@app.route("/TerminerExercice", methods=['POST'])
def terminer_exercice():
    data = request.get_json()  # get the data sent in the request
    module_number = data['moduleNumber']
    exercice = data['exercice']
    exercice_number = int(data['exercice'][-1])
    # process the data
    # Define the spreadsheet ID and range
    RANGE_NAME = values[session['programmeNumber']][0] + '!A2:ZZ'  # Include all columns and rows
    # Fetch the data from the Google Sheets API
    creds = service_account.Credentials.from_service_account_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    
    # loop through each row of the sheet data
    for i, row in enumerate(result['values']):
        # check if the second column contains the exercice string and the last character of the first column is the module_number
        today = datetime.date.today().isoformat()
        if row[1] == exercice and row[0][-1] == module_number:
            if row[10] == "exercice avec date de début" or row[10] == "exercice avec date de début et date de fin prévisionnelle":
                result['values'][i][9] = today
            result['values'][i][5] = "terminé"

    # update the spreadsheet with the modified data
    body = {
        'values': result['values']
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()

    
    return 'Data received',200

@app.route("/login")
def login():
    session["logged_in"] = False
    authorization_url, state = flow.authorization_url()
    print(authorization_url, state)
    session["state"] = state
    session["logged_in"] = True 
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
    session["logged_in"] = False
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run()
