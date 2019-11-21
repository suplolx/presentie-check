import os.path
import sys
from secret import folder_id

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import pickle
import pandas as pd


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
        return df


def presentie(naam, file_id):
    df = get_data(file_id)
    # Searching for correct name and returning tuple of data
    for row in df[["Deelnemers", "Dagdelen", "Aanwezig", 
                    "Afwezig", "Afgemeld", "% Aanwezig"]].itertuples():
        if row.Deelnemers == naam:
            return (row.Deelnemers, row._6)


def main(input_naam, weeks):
    if int(weeks) > 10:
        print("Sorry, het maximale aantal weken is 10.")
        sys.exit(0)
    # Initialise sheets app
    app = client_auth('drive', "v3")

    # Creating a query for selecting the right folder in Google Drive
    query=f"'{folder_id}' in parents"

    response = app.files().list(q=query,
                                    spaces='drive',
                                    fields='files(id, name, parents)').execute()

    # Retrieving all files in the folder and sorting them by week number
    files = response.get("files", [])
    files_sorted = sorted(files, key=lambda i: i['name'], reverse=True)

    # Looping through files searching for given name and week range
    for file in files_sorted[0:int(weeks)]:
        # Excluding template file from data
        if file["name"] != "Presentie Lijst Template":
            print(f"{file['name']}: {presentie(input_naam, file['id'])}")


if __name__ == "__main__":
    naam = input("Naam deelnemer: ")
    weken = input("Aantal weken (max 10): ")
    main(naam, weken)
