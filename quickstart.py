from __future__ import print_function
import httplib2
import os
import unicodedata

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
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
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
    spreadsheetId = '1RNNyvtmW0dbSzVTew_FyoUsfYmQOmvMoNH_FeP_yAn4'
    # file_list = list_files(service, spreadsheetId)
    # print(file_list)
    # file_contents = read_file(service, spreadsheetId, '1') # get the file data for row 1
    # print(file_contents)
    add_file(service, spreadsheetId, "007", "filename07.jpg", "sevensevensevensevensevensevensevenseven")

def list_files(service, spreadsheetId):
    rangeName = 'Sheet1!B1:B'
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        fileList = []
        for row in values:
            for cell in row:
                cellData = unescape_cell(cell)
                fileList.append(cellData)
        return fileList


"""
current_comment = file_post.add_comment(encryption[:10000])
encryption = encryption[10000:]

#if it does not fit, then we will add a child comment to it and repeat
if len(encryption) != 0:

    while len(encryption) > 10000:
        #to-do
        current_comment = current_comment.reply(encryption[:10000])
        encryption = encryption[10000:]

if len(encryption) > 0:
    current_comment.reply(encryption)
"""

def add_file(service, spreadsheetId, id, filename, data):
    """
    TODO: just the example code for now
    """
    # The A1 notation of a range to search for a logical table of data.
    # Values will be appended after the last row of the table.
    rangeName = 'Sheet1!A1:ZZZ'

    value_input_option = 'RAW'

    insert_data_option = 'INSERT_ROWS'

    # [fileid, filename, data...]
    fileRow = [escape_cell(id), escape_cell(filename)]

    current_cell = data[:MAX_USABLE_CELL]
    fileRow.append(escape_cell(current_cell))
    data = data[MAX_USABLE_CELL:]
    while len(data) > MAX_USABLE_CELL:
        current_cell = data[:MAX_USABLE_CELL]
        fileRow.append(escape_cell(current_cell))
        data = data[MAX_USABLE_CELL:]

    values = [
        fileRow
    ]

    value_range_body = {
        'values': values
    }
    request = service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId,
        range=rangeName,
        valueInputOption=value_input_option,
        insertDataOption=insert_data_option,
        body=value_range_body
    )
    response = request.execute()

def read_file(service, spreadsheetId, fileId):
    row = file_id_to_row(service, spreadsheetId, fileId)
    return read_file(service, spreadsheetId, row)

def file_id_to_row(service, spreadsheetId, id):
    """
    TODO: this might require another query but we probably dont want to do that...
    """

def read_file(service, spreadsheetId, row):
    """
    read the file stored in the associated row
    """
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
    cellData = cell[1:]
    normalizedCellData = unicodedata.normalize('NFKD', cellData).encode('ascii','ignore')
    return normalizedCellData

def escape_cell(data):
    # assert data length is less or equal to MAX_USABLE_CELL
    return "`" + data

if __name__ == '__main__':
    main()
