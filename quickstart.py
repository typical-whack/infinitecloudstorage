from __future__ import print_function
import httplib2
import os
import unicodedata

import crypt

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from math import *

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

KEY = "PASSWORD"
FERNET_CIPHER = crypt.FernetCipher(KEY)

MAX_CELL = 50000
MAX_USABLE_CELL = MAX_CELL - 1 # since we have an escape character at the front
MAX_COLUMNS = 256
MAX_CELLS = 2000000
MAX_ROWS = 7812 # MAX CELLS / MAX COLUMNS

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
    spreadsheetId = '1RNNyvtmW0dbSzVTew_FyoUsfYmQOmvMoNH_FeP_yAn4' # directory sheet
    # file_list = list_files(service, spreadsheetId)
    # print(file_list)
    # file_contents = read_file(service, spreadsheetId, '1') # get the file data for row 1
    # print(file_contents)
    # add_file(service, spreadsheetId, "008", "filename08.txt", "eighteighteighteighteighteight")
    # file_contents = read_file(service, spreadsheetId, '8') # get the file data for row 8
    # print(file_contents)
    # add_spreadsheet(service)
    dataSpreadsheetId = "1Dcbbqtvw_ReiPbJ7LQ9Y7RxXS95sO7AWDfQrB1ilZ84"
    # create_directory_entry(service, spreadsheetId, "009", "testcreatedirent.txt", "2560", "2017-03-25T15:32:23+00:00", dataSpreadsheetId)
    # with open("mobydick.txt", 'rb') as fo:
    #     plaintext = fo.read()
    # write_data(service, dataSpreadsheetId, plaintext)
    print(read_file(service, dataSpreadsheetId))

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

def add_file(service, spreadsheetId, fileid, filename, size, date, data):
    dataSpreadsheetId = add_spreadsheet(service)
    create_directory_entry(service, spreadsheetId, fileid, filename, size, date, dataSpreadsheetId)
    write_data(service, dataSpreadsheetId, data)

def write_data(service, spreadsheetId, data):
    rangeName = 'Sheet1!A1:ZZZ'
    value_input_option = 'RAW'
    insert_data_option = 'INSERT_ROWS'

    encrypted_data = FERNET_CIPHER.encrypt(data)
    totalDataCells = int(ceil(float(len(encrypted_data)) / float(MAX_USABLE_CELL)))
    print(len(encrypted_data))
    print(totalDataCells)

    fileRow = []
    for i in range(totalDataCells):
        current_cell = encrypted_data[:MAX_USABLE_CELL]
        fileRow.append(escape_cell(current_cell))
        encrypted_data = encrypted_data[MAX_USABLE_CELL:]
        if i % 256 is 0 and i is not 0:
            write_row(service, spreadsheetId, fileRow)
            fileRow = []
    # write the last row, if it wasnt a length of 256
    write_row(service, spreadsheetId, fileRow)

def write_row(service, spreadsheetId, rowData):
    # expecting rowData to be a list of string. each string with a length of 50000 or less
    # the entire list being of length 256 or less.
    # each string is escaped with a `
    rangeName = 'Sheet1!A1:ZZZ'
    value_input_option = 'RAW'
    insert_data_option = 'INSERT_ROWS'
    values = [
        rowData
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

def create_directory_entry(service, spreadsheetId, fileid, filename, size, date, dataSpreadsheetId):
    rangeName = 'Sheet1!A1:E'
    value_input_option = 'RAW'
    insert_data_option = 'INSERT_ROWS'
    # [fileid, filename, size, date, dataSpreadsheetId]
    fileRow = [
        escape_cell(fileid),
        escape_cell(filename),
        escape_cell(size),
        escape_cell(date),
        escape_cell(dataSpreadsheetId)
    ]
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

def add_spreadsheet(service):
    spreadsheet_body = { }
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    return response[spreadsheetId]

def read_file(service, spreadsheetId, fileId):
    row = file_id_to_row(service, spreadsheetId, fileId)
    return read_file(service, spreadsheetId, row)

def file_id_to_row(service, spreadsheetId, id):
    """
    TODO: this might require another query but we probably dont want to do that...
    """

def read_file(service, spreadsheetId):
    joinedData = ""
    for row in range(1, MAX_ROWS):
        isData, data = read_row(service, spreadsheetId, row)
        if not isData:
            return joinedData
        joinedData += data
    return joinedData


def read_row(service, spreadsheetId, row):
    rangeName = 'Sheet1!' + "A" + str(row) + ":" + str(row)
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        return False, ""
    else:
        for row in values:
            joinedData = ""
            for cell in row:
                cellData = unescape_cell(cell)
                joinedData = joinedData + cellData
            decrypted_data = FERNET_CIPHER.decrypt(joinedData)
            return True, decrypted_data

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
