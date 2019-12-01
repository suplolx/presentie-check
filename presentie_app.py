import os.path
import sys
from datetime import datetime
from secret import folder_id

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pickle
import pandas as pd
import jinja2
import pdfkit


templateloader = jinja2.FileSystemLoader(searchpath="./template")
template_env = jinja2.Environment(loader=templateloader)
TEMPLATE_FILE = "template.html"
template = template_env.get_template(TEMPLATE_FILE)

config_path = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

t_format = "%d-%m-%Y %H:%M:%S"


# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly', 
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]


def client_auth(app, version):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # Returning client instance of requested app (e.g sheets, drive, docs)
    return build(app, version, credentials=creds)


def get_data(spreadsheet_id):
    # Initialise sheets app
    app = client_auth('sheets', "v4")
    
    gsheet = app.spreadsheets().values().get(spreadsheetId=spreadsheet_id, 
                                             range="Lijst").execute()
    print("Data sheet ingeladen...")
    # Setting header on row 3
    header = gsheet.get('values', [])[2]
    # Everything else is data
    values = gsheet.get('values', [])[3:]

    if not values:
        print('Geen data gevonden')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                # Breaking if the end of the list is reached
                if row[0] != 'Nieuw':
                    column_data.append(row[col_id])
                else:
                    break
            # Creating pandas dataframe
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        print("Data omgezet in dataframe...")
        return df


def presentie(naam, file_id):
    df = get_data(file_id)
    # Searching for correct name and returning tuple of data
    for row in df[["Deelnemers", "Dagdelen", "Aanwezig", 
                    "Afwezig", "Afgemeld", "% Aanwezig"]].itertuples():
        if row.Deelnemers == naam:
            return (row.Deelnemers, row.Aanwezig, row.Afwezig, row.Afgemeld, row._6)


def get_presentie_data(input_naam, weeks):
    if int(weeks) > 10:
        print("Sorry, het maximale aantal weken is 10.")
        sys.exit(0)
    # Initialise sheets app
    service = client_auth('drive', "v3")

    # Creating a query for selecting the right folder in Google Drive
    query=f"'{folder_id}' in parents"

    response = service.files().list(q=query,
                                    spaces='drive',
                                    fields='files(id, name, parents)').execute()

    # Retrieving all files in the folder and sorting them by week number
    files = response.get("files", [])
    files_sorted = sorted(files, key=lambda i: i['name'], reverse=True)

    data_list = list()

    # Looping through files searching for given name and week range
    for file in files_sorted[0:int(weeks)]:
        # Excluding template file from data
        if file["name"] != "Presentie Lijst Template":
            presentie_data = presentie(input_naam, file['id'])
            data_list.append(
                {
                    "week_nummer": file['name'], 
                    "aanwezig": presentie_data[1],
                    "afwezig": presentie_data[2],
                    "afgemeld": presentie_data[3],
                    "aanwezig_p": presentie_data[4]
                }
            )
            print(f"Data van {file['name']} verwerkt..")
    template_data = template.render(presentie=data_list, naam=input_naam, datum=datetime.now().strftime(t_format))
    html_file = open("test.html", 'w')
    html_file.write(template_data)
    html_file.close()
    pdfkit.from_file("test.html", f"./rapporten/{input_naam} {data_list[-1]['week_nummer']} tm {data_list[0]['week_nummer']}.pdf", configuration=config_path)
    return data_list
