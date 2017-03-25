from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

MAX_CELL = 50000
MAX_USABLE_CELL = MAX_CELL - 1 # since we have an escape character at the front

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """
    Shows basic usage of the Sheets API.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    file_contents = read_file(service, '1') # get the file data for row 1
    print(file_contents)

def list(service):
    """
    lists all of the files in the current sheet and their associated IDs
    """
    spreadsheetId = '1RNNyvtmW0dbSzVTew_FyoUsfYmQOmvMoNH_FeP_yAn4'
    rangeName = 'Sheet1!A1:B'
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('ID, Filename:')
        for row in values:
            print('%s, %s' % (row[0], row[1]))

def add_file(service, id, filename, data):
    """
    TODO: just the example code for now
    """
    spreadsheetId = '1RNNyvtmW0dbSzVTew_FyoUsfYmQOmvMoNH_FeP_yAn4'
    # The A1 notation of a range to search for a logical table of data.
    # Values will be appended after the last row of the table.
    range_ = ''  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = ''  # TODO: Update placeholder value.

    # How the input data should be inserted.
    insert_data_option = ''  # TODO: Update placeholder value.

    value_range_body = {
        # TODO: Add desired entries to the request body.
    }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()

def read_file(service, id):
    row = file_id_to_row(service, id)
    return read_file(service, row)

def file_id_to_row(service, id):
    """
    TODO: this might require another query but we probably dont want to do that...
    """

def read_file(service, row):
    """
    read the file stored in the associated row
    """
    spreadsheetId = '1RNNyvtmW0dbSzVTew_FyoUsfYmQOmvMoNH_FeP_yAn4'
    rangeName = 'Sheet1!' + "C" + row + ":1"
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            joinedData = ""
            for cell in row:
                cellData = unescape_cell(cell)
                joinedData = joinedData + cellData
            return joinedData

def unescape_cell(cell):
    # assert cell[0] is "`", "cell that you're trying to unescape isn't escaped!"
    return cell[1:]

def escape_cell(data):
    # assert data length is less or equal to MAX_USABLE_CELL
    return "`" + data

if __name__ == '__main__':
    main()
